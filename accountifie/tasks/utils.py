import sys, os, cPickle, base64, functools, subprocess, traceback, hashlib
from datetime import tzinfo, timedelta, datetime
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.models import User

from accountifie.middleware.docengine import getCurrentUser

import logging
logger = logging.getLogger('default')


__all__=tuple(
    '''task utc utcnow initialCmd initialCmdStr pid2cmdline hashFunc'''.split()
    )

ZERO = timedelta(0)

class TaskError(Exception):
    pass

class TaskLimitError(TaskError):
    pass

class TaskStdout(str):
    def __new__(cls,v,pid):
        self = str.__new__(TaskStdout,v)
        self.pid = pid
        return self

# A UTC class.
class utc(tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO
utc = utc()

def utcnow():
    u = datetime.utcnow()
    return u.replace(tzinfo=utc)

def encode(obj):
    return base64.b64encode(cPickle.dumps(obj))

def decode(s):
    return cPickle.loads(base64.b64decode(s))

def hashFunc(task,args,kwds):
    if isinstance(args,tuple):
        args = encode(args)
    if isinstance(kwds,dict):
        kwds = encode(tuple([(k,kwds[k]) for k in sorted(kwds.iterkeys())]))
    return hashlib.md5(task+args+kwds).hexdigest()

def find_manage_py():
    m = getattr(settings,'MANAGE_PY',None)
    if m: return m
    for x in 'ENVIRON PROJECT'.split():
        x = getattr(settings,x+'_DIR',None)
        if not x: continue
        m = os.path.join(x,'manage.py')
        if os.path.isfile(m):
            return m
    raise valueError('cannot find manage.py')

def find_python(exe):
    m = getattr(settings,'PYTHON',None)
    if m: return x
    p = 'python.exe' if sys.platform=='win32' else 'python'
    if os.path.split(exe)[-1].lower()==p: return exe
    exe = os.path.join(os.path.dirname(exe),p)
    if os.path.isfile(exe): return exe
    for x in 'ENVIRON PROJECT'.split():
        x = getattr(settings,x+'_DIR',None)
        if not x: continue
        m = os.path.join(x,'bin',p)
        if os.path.isfile(m):
            return m
    raise ValueError('cannot find python executable')


def initialCmd(task):
    return [find_python(sys.executable),find_manage_py(), 'run_task', '--task=%s' % task]


def initialCmdStr(task):
    return ' '.join(initialCmd(task))

def pid2cmdline(pid):
    try:
        fname = "/proc/%s/cmdline" % pid
        with open(fname, "rt") as f:
            return ' '.join([x for x in f.read().split('\x00') if x])
    except:
        # am I in OSX?
        proc = subprocess.Popen(["ps", "-Eww", "%d" % pid],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        try:
            return '/'+out.split('/',1)[1]
        except:
            return ''

def task(f=None,errorOnDuplicate=False):
    '''
    special case arguments
    task_log_std    True copy the stdout/err to the deferredtasks.out
                    default False or settings.TASK_LOG_STD
    task_testing    testing mode, default False or settings.testing
    task_sync       True-->don't detach the run_task management command
                    default False or settings.TASK_SYNC
    '''
    
    if f is None:
        def wrapper(f):
            return task(f,errorOnDuplicate=errorOnDuplicate)
    else:
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            from .models import DeferredTask
            n = DeferredTask.objects.filter(finished=False).count()
        
            limit = getattr(settings,'DOCENGINE_TASKS_LIMIT',10)
            if n>=limit:
                raise TaskLimitError('Number of unfinished tasks, %d, has reached limit, %d!' % (n,10))

            #delete ancient tasks
            ancient = utcnow()-timedelta(seconds=getattr(settings,'DOCENGINE_TASKS_EXPIRE_SECONDS',24*7*3600))
            DeferredTask.objects.filter(finished=True,finish__lt=ancient).delete()
            task = '.'.join((f.__module__,f.func_name))
            ae = encode(args)
            ke = encode(kwds)
            if errorOnDuplicate:
                try:
                    hashcode=hashFunc(task,ae,kwds)
                    dtask = DeferredTask.objects.get(finished=False,hashcode=hashcode)
                    raise TaskError('Task %3d: pid=%s %s with duplicate hashcode %s found!' % (dtask.id,dtask.pid,task,hashcode))
                except DeferredTask.DoesNotExist:
                    pass

            try:
                user = getCurrentUser()
                username = getattr(user, User.USERNAME_FIELD)
            except:
                username = ''
            ARGS = initialCmd(task) + ['--args=%s'%ae, '--kwds=%s'%ke, '--username=%s' % encode(username)]
            
            testing = kwds.pop('task_testing',getattr(settings,'TESTING',False))
            sync = kwds.pop('task_sync',getattr(settings,'TASK_SYNC',False))
            log_std = kwds.pop('task_log_std',getattr(settings,'TASK_LOG_STD',False))
            if testing: ARGS.append('--task-testing')
            if sync: ARGS.append('--task-sync')
            if log_std: ARGS.append('--task-log-std')

            def error_task(out,err,msg):
                _success_url = kwds.get('success_url', False)
                dtask = DeferredTask()
                dtask.pid = os.getpid()
                dtask.task = task
                dtask.start = dtask.finish = utcnow()
                dtask.success = False
                dtask.finished = True
                dtask.stdout = out
                dtask.stderr = err
                dtask.args = repr(args)
                dtask.kwds = repr(kwds)
                dtask.status = 'unstarted'
                dtask.progress = 0
                dtask.success_url = ''
                if _success_url and not '?pid=' in _success_url:
                    if '?' in _success_url:
                        dtask.success_url = "%s&pid=%s" % (_success_url, dtask.pid)
                    else:
                        dtask.success_url = "%s?pid=%s" % (_success_url, dtask.pid)
                dtask.save()
                raise TaskError(msg)
            
            try:
                p = subprocess.Popen(ARGS,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
                out, err = p.communicate()
                c = p.returncode
                if c:
                    error_task(out,err,'subprocess call to run_task failed with status code %s' % c )
                else:
                    #try to check the expected output for PID
                    try:
                        pid = int(out)
                    except:
                        s = out.strip()
                        i = len(s)-1
                        while i>=0 and s[i] in '0123456789':
                            i -= 1
                        try:
                            pid = int(s[i+1:])
                        except:
                            pid = None
                    if not (pid and pid2cmdline(pid).startswith(initialCmdStr(task))):
                        msg = '!!!!! Could not determine task %s pid from  deferred process stdout\n!!!!! --- start\n%s\n!!!!! --- end' % (task, utcnow())
                        if err:
                            err += '\n'+msg
                        else:
                            err = msg
                        c = 666
                    else:
                        out = TaskStdout(out,pid)
                return c,out,err
            except:
                err = StringIO()
                traceback.print_exc(file=err)
                logger.info(err)
                logger.info(traceback.format_exc())
                # FIXME: next line looks buggy as error_taks wont take None as
                # stdout
                error_task(None,err.getvalue(),'subprocess call to run_task failed with traceback')
        wrapper._task_func = f
    return wrapper
