from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django import db

from optparse import make_option
import sys, os, time, traceback
from accountifie.tasks.models import DeferredTask
from accountifie.tasks.utils import decode, utcnow, hashFunc
from StringIO import StringIO

import logging
logger = logging.getLogger('default')

class IdentiFile(object):
    '''utility file class that flushes itself after lines are written'''
    def __init__(self,f,i):
        self._f = f
        self._sol = True
        self._i = i

    def __getattr__(self,a):
        return getattr(self._f,a)

    def write(self,s):
        i = '%s:%s:' % (self._i,time.strftime("%Y%m%d%H%M%S",time.gmtime(time.time())))
        w = self._f.write
        if self._sol: w(i)
        if '\n' not in s:
            w(s)
            self._sol = False
        else:
            self._sol = s.endswith('\n')
            if self._sol:
                s = s[:-1]
            w(s.replace('\n','\n'+i))
            if self._sol: w('\n')
            self._f.flush()

class Detacher(object):
    _daemon = False
    if sys.platform!='win32':
        @classmethod
        def detach(cls):
            import signal
            try:
                # Fork a child process so the parent can exit.  This will return control
                # to the command line or shell.  This is required so that the new process
                # is guaranteed not to be a process group leader.  We have this guarantee
                # because the process GID of the parent is inherited by the child, but
                # the child gets a new PID, making it impossible for its PID to equal its
                # PGID.
                pid = os.fork()
            except OSError, e:
                return e.errno, e.strerror    # ERROR (return a tuple)
            if (pid == 0):       # The first child.
                # Next we call os.setsid() to become the session leader of this new
                # session.  The process also becomes the process group leader of the
                # new process group.  Since a controlling terminal is associated with a
                # session, and this new session has not yet acquired a controlling
                # terminal our process now has no controlling terminal.  This shouldn't
                # fail, since we're guaranteed that the child is not a process group
                # leader.
                os.setsid()

                # When the first child terminates, all processes in the second child
                # are sent a SIGHUP, so it's ignored.
                signal.signal(signal.SIGHUP, signal.SIG_IGN)

                try:
                    # Fork a second child to prevent zombies.  Since the first child is
                    # a session leader without a controlling terminal, it's possible for
                    # it to acquire one by opening a terminal in the future.  This second
                    # fork guarantees that the child is no longer a session leader, thus
                    # preventing the daemon from ever acquiring a controlling terminal.
                    pid = os.fork()        # Fork a second child.
                except OSError, e:
                    return e.errno, e.strerror  # ERROR (return a tuple)

                if (pid == 0):      # The second child.
                    if cls._daemon:
                        # Ensure that the daemon doesn't keep any directory in use.  Failure
                        # to do this could make a filesystem unmountable.
                        os.chdir("/")
                        # Give the child complete control over permissions.
                        os.umask(0)
                else:
                    sys.stdout.flush()
                    sys.stdout.write(str(pid))
                    sys.stdout.flush()
                    os._exit(0)      # Exit parent (the first child) of the second child.
            else:
                os._exit(0)         # Exit parent of the first child.
            # Close all open files.  Try the system configuration variable, SC_OPEN_MAX,
            # for the maximum number of open files to close.  If it doesn't exist, use
            # the default value (configurable).
            try:
                maxfd = os.sysconf("SC_OPEN_MAX")
            except (AttributeError, ValueError):
                maxfd = 256       # default maximum
            maxfd=16
            for fd in range(0, maxfd):
                try:
                    os.close(fd)
                except OSError:   # ERROR (ignore)
                    pass
            # Redirect the standard file descriptors to /dev/null.
            null = '/dev/null'
            os.open(null, os.O_RDONLY)  # standard input (0)
            os.open(null, os.O_RDWR)    # standard output (1)
            os.open(null, os.O_RDWR)    # standard error (2)
            return 0

    if sys.platform=='win32':
        @classmethod
        def detach(cls):
            script = sys.argv[0]
            sys.argv.append('--detached')
            if special in sys.argv:
                sys.argv.remove(special)
                return 0 #we're in the child just return

            #we're in the parent do stuff
            try:
                from subprocess import CreateProcess
                class STARTUPINFO:
                    dwFlags = 0
                    hStdInput = None
                    hStdOutput = None
                    hStdError = None
                class pywintypes:
                    error = IOError
            except ImportError:
                try:
                    from win32process import CreateProcess, STARTUPINFO
                except ImportError:
                    return 1, "Can't import CreateProcess from subprocess or win32process"
            exe = sys.executable.replace('n.exe','nw.exe')
            startupinfo = STARTUPINFO()
            args = ''.join([' "%s"' % a for a in sys.argv[1:]])
            cmd = '"%s" "%s"%s %s' % (exe,script,args,special)
            try:
                hp, ht, pid, tid = CreateProcess(None, cmd,
                                                # no special security
                                                None, None,
                                                0,  #don't inherit standard handles
                                                0x208,
                                                None,
                                                None,
                                                startupinfo)
            except pywintypes.error, e:
                return 2, str(e)
            sys.stdout.write(str(pid))
            sys.stdout.flush()
            os._exit(0)         #Exit parent

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--task', action='store', dest='task', help='python module path'),
        make_option('--args', action='store', dest='args', help='arguments'),
        make_option('--kwds', action='store', dest='kwds', help='keyword arguments'),
        make_option('--username', action='store', dest='username', help='username'),
        make_option('--task-testing', action='store_true', dest='testing', default=False, help='use test mode'),
        make_option('--task-sync', action='store_false', dest='async', default=True, help='don\'t detach'),
        make_option('--task-log-std', action='store_true', dest='log_std', default=False, help='copy stdout/stderr to task log'),
        ) + ((make_option('--detached', action='store_true', dest='detached',
                default=False, help='detached signifier for windows only'),)
                if sys.platform=='win32' else ())

    def handle(self, **options):
        taskName = options['task']
        if not taskName: raise ValueError('required argument --task not specified')
        async = options['async']
        
        if async:
            D = Detacher()
            if sys.platform=='win32':
                if not options['detached']:
                    D.detach()
            else:
                D.detach()

            #if we're here we should be fully detached
        #if --task-testing was passed we use a test setup
        if options['testing']:
            from django.test.utils import setup_test_environment
            setup_test_environment()
        pid = os.getpid()
        logs = os.path.join(settings.ENVIRON_DIR,'logs')
        if not os.path.isdir(logs):
            os.makedirs(logs)
        log = IdentiFile(open(os.path.join(logs,'deferredtasks.out'),'a'),'%-5d' %pid)
        success = False
        print >> log, '##### task %s[%-5d] started' % (taskName,pid)
        try:
            if options['log_std']:
                #debug version everything get's written to the logfile as well
                class StringIOX(StringIO):
                    def write(self,s):
                        log.write(s)
                        StringIO.write(self,s)
                sys_stdout = StringIOX()
                sys_stderr = StringIOX()
            else:
                sys_stdout = StringIO()
                sys_stderr = StringIO()
            if not async:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
            sys.stdout = sys_stdout
            sys.stderr = sys_stderr
            dtask = DeferredTask()
            dtask.start = utcnow()
            dtask.pid = pid
            dtask.progress = 0
            username = options.get('username','')
            dtask.username = decode(username) if username else ''
            dtask.status = 'initialized'


            # reset DB connection which might have been killed in detachment process
            # but close_connection deprecated in Django 1.8
            # seems to be working OK without this
            #db.close_connection()
            
            dtask.save()
            D = {}
            dtask.task = taskName
            dtask.save()
            exec 'from %s import %s as task' % tuple(taskName.rsplit('.',1)) in D
            task = D['task']
            args = options.get('args',())
            if args: args = decode(args)
            kwds = options.get('kwds',{})
            if kwds: kwds = decode(kwds)
            _success_url = kwds.pop('task_success_url', False)
            dtask.success_url = ''
            if _success_url and not '?pid=' in _success_url:
                if '?' in _success_url:
                    dtask.success_url = "%s&pid=%s" % (_success_url, dtask.pid)
                else:
                    dtask.success_url = "%s?pid=%s" % (_success_url, dtask.pid)
            dtask.args=repr(args)
            dtask.kwds=repr(kwds)
            dtask.hashcode = hashFunc(taskName,args,kwds)
            dtask.title = kwds.pop('task_title','')
            dtask.status = 'prepared'
            dtask.save()
            result = getattr(task,'_task_func',task)(*args,**kwds)
            dtask = DeferredTask.objects.get(pid=pid)
            dtask.result = result
            dtask.status = 'finished'
            dtask.progress = 100
            dtask.save()
            success = True
        except:
            traceback.print_exc()
            traceback.print_exc(file=log)
        finally:
            try:
                dtask = DeferredTask.objects.get(pid=pid)
                dtask.success = success
                dtask.finished = True
                dtask.status = 'suceeded' if success else 'failed'
                dtask.finish = utcnow()
                dtask.stdout = sys_stdout.getvalue()
                dtask.stderr = sys_stderr.getvalue()
                dtask.save()
                print >> log, '%s task %s[%-5d] %s' % (('!!!!!','#####')[success],taskName,pid,('failed!','ended OK.')[success])
            except:
                traceback.print_exc(file=log)
            finally:
                if not async:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
