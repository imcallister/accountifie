"""
Adapted with permission from ReportLab's DocEngine framework
"""



import os

from datetime import timedelta
from decimal import Decimal
from collections import namedtuple
from subprocess import Popen, PIPE
from django.conf import settings
from importlib import import_module


def run_shell_command(command, cwd):
    """
    Run command in shell and return results.
    """
    p = Popen(command, shell=True, cwd=cwd, stdout=PIPE, stderr=PIPE)
    stdout = p.communicate()[0]
    if stdout:
        stdout = stdout.strip()
    return stdout

_ntuple_diskusage = namedtuple('usage', 'total used free percentage')


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


# as per http://stackoverflow.com/questions/4274899/get-actual-disk-space
def disk_usage(path):
    
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    percentage = "%.2f" % (float(used)/float(total)*100) # make sure displays naturally with 2 decimal places
    percentage = Decimal(percentage)
    return _ntuple_diskusage(sizeof_fmt(total), sizeof_fmt(used), sizeof_fmt(free), percentage)


def server_uptime():
    uptimeString = 'unknown'
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))
    return uptime_string
    

def folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += folder_size(itempath)
    return total_size


def loggers():
    LOGGING_APPS_START = ('docengine', os.path.basename(settings.PROJECT_DIR) )
    

def get_available_stats():
    "Finds apps with a stats.py, gets back the dictionary contents"
    found = []
    for app_name in settings.INSTALLED_APPS:
        try:
            stats = import_module('.stats', app_name)
            if hasattr(stats, 'SQL_QUERIES'):
                for (stat_name, help_text, query) in stats.SQL_QUERIES:
                    found.append(
                        dict(app_name=app_name, 
                            stat_name=stat_name, 
                            help_text=help_text, 
                            query=query)
                        )
        except ImportError:
            continue
    return found

def get_configuration_warnings():
    "Checks a bunch of things which were not in docengine earlier but are now"
    warnings = []


    for (filename, caution) in [
        ('project/static/css/base.css', 
            """Allows you to override the CSS for your site, including templates
            provided by docengine itself.  An empty file will do."""),
        ('project/templates/base.html', 
            """Allows you to determine the HTML template for your site.  Docengine
            will expect to find this somewhere.  The minimum it needs to contain is:  {% extends 'common/base.html' %}"""),

        ]:
        expected_file_name = os.path.join(settings.ENVIRON_DIR, filename)
        if not os.path.isfile(expected_file_name):
            warnings.append(("Missing file", filename, caution))
    return warnings




