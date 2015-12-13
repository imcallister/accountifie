import re, os
from optparse import make_option
from shutil import copytree, rmtree

from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.startapp import Command as StartAppCommand


class Command(StartAppCommand):
    help = ("Creates a Django app directory structure for the given app "
            "name in the current directory or optionally in the given "
            "directory.")
    option_list = StartAppCommand.option_list + (
        make_option('--base',
                action='store', dest='base',
                help='The Docengine base app name to be cloned'),
        )
                    
    def handle(self, app_name=None, target=None, **options):
        # prepend the full path of the docengine folder to the template app name
        base = options.get('base', None)
        if base is None:            
            raise CommandError('You must specify a base application name to clone from within Docengine')
        cwd = os.getcwd()
        os.chdir(settings.PROJECT_DIR)
        options['template'] = os.path.join(os.environ['HOME'],'code','docengine', 'docengine', 'samples', base)
        del options['base']
        super(Command, self).handle(app_name=app_name, target=target, **options)
        
        # add the app_name to settings.INSTALLED_APPS
        settings_file = open('settings.py')
        settings_contents = settings_file.read()
        settings_file.close()
        pattern = r'(INSTALLED_APPS =[^)]+)'
        re_pattern = re.compile(pattern)
        try:
            installed_apps_chunk = re_pattern.findall(settings_contents)[0]
            # the following is rather optimistic: assumes there is no
            # closing parenthesis anywhere within settings.INSTALLED_APPS tuple
            # and that 'INSTALLED_APPS =' shows exactly once in the text
            result = re.sub(pattern, "%s    'project.%s',\n" % (installed_apps_chunk, app_name), settings_contents)
            settings_file = open('settings.py', 'w')
            settings_file.write(result)
            settings_file.close()
        except:
            self.stdout.write("\n         Could not update 'settings.py'.\
 Please add '%s' to the INSTALLED APPS list\n"  % app_name)
        user_media = os.path.join(settings.ENVIRON_DIR, 'media', '%s' % app_name)
        base_user_media = os.path.join(settings.PROJECT_DIR, '%s' % app_name, 'media')
        # move any existing app_name/media to user /media/app_name
        if os.path.isdir(base_user_media):
            copytree(base_user_media, user_media)
            rmtree(base_user_media)
        # make certain that basic user media structure is there
        if not os.path.isdir(os.path.join(user_media, 'fonts')):
            os.makedirs(os.path.join(user_media, 'fonts'))
        if not os.path.isdir(os.path.join(user_media, 'resources')):
            os.makedirs(os.path.join(user_media, 'resources'))
        if not os.path.isdir(os.path.join(user_media, 'styles')):
            os.makedirs(os.path.join(user_media, 'styles'))
        os.chdir(cwd)
