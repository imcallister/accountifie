"""
Adapted with permission from ReportLab's DocEngine framework
"""

import re, os, sys
from collections import OrderedDict
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.shortcuts import render
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseServerError
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from accountifie.common.models import Log
from accountifie.common.dbutils import all_relations, all_concrete_models

from . import utils


LOG_ENTRIES_PER_PAGE = 25

def localsets():
    res = {}
    project_name = os.path.basename(settings.PROJECT_DIR)
    try:
        ls = __import__('%s.localsettings' % project_name)
        for k, v in list(ls.localsettings.__dict__.items()):
            if k == k.upper() and re.match("[^__]", k):
                res[k]=v
    except:
        pass
    return res

def settings_list():
    res = []
    omit_list = ('SECRET_KEY', 'DB_PASSWORD',)
    for ke, va in [ (k, v) for k, v in list(settings._wrapped.__dict__.items()) if not k.startswith('_') and k not in omit_list]:
        if ke=='DATABASES':
            for name, props in list(settings.DATABASES.items()):
                res.append(('DATABASE "%s"' % name, props['NAME']),)
        else:
            if va:
                res.append((ke, va),)
    return res

@staff_member_required
def index(request):
    pip = os.path.join(sys.exec_prefix, 'bin', 'pip')
    if not os.path.isfile(pip):
        pip = 'pip'
    SHELL_COMMANDS = (
        ('Hostname','hostname'),
        ('hg version', 'hg id'),
        ('git version', "git log --pretty=format:'%h' -n 1"),
        ('hg branch', 'hg branch'),
        ('git branch', 'git rev-parse --abbrev-ref HEAD'),
        ('MySQL version', 'mysql --version'),
        ('Local Packages', '%s freeze -l' % pip)
    )
    SD = OrderedDict()
    for k,v in sorted(settings_list(), key=lambda x: x[0]):
        SD[k] = v
    context = RequestContext(request, {
        'args': sys.argv,
        'exe': sys.executable,
        'settings': SD,
        })

    context['versions'] = OrderedDict()
    # get versions
    curr_dir = os.path.realpath(os.path.dirname(__file__))
    for name, shell_command in SHELL_COMMANDS:
        try:
            result = utils.run_shell_command(shell_command, curr_dir)
            if result:
                if isinstance(result, list):
                    result = '<br>'.split(result)
                context['versions'][name] = result
        except:
            pass
    # machine status
    context['machine'] = OrderedDict()
    if sys.platform == 'darwin':
        context['machine']['Uptime'] = 'not done yet on MacOS'
        context['machine']['Disk Space'] = 'not done yet on MacOS'
    elif sys.platform == 'win32':
        context['machine']['Uptime'] = 'not done yet on Windows'
        context['machine']['Disk Space'] = 'not done yet on Windows'
    else:
        context['machine']['Uptime'] = utils.server_uptime()
        context['machine']['Disk Space'] = utils.disk_usage('/')._asdict()
    if os.path.exists(settings.MEDIA_ROOT):
        context['machine']['Media Folder'] = utils.sizeof_fmt(utils.folder_size(settings.MEDIA_ROOT))

    context['stats'] = utils.get_available_stats()

    gan = lambda app: app
    context['apps'] = [(gan(app), ', '.join([model.__name__ for model in models])) for app, models in all_concrete_models()]
    context['relations'] = [[(model.__name__, ', '.join(['%s (%s) through %s' % (relation.__name__, relation.__module__, field.__class__.__name__)
                                                        for field, relation in relations]), gan(app))
                                                            for model, relations in rel_info]
                                                                for app, rel_info in all_relations()]
    #context['rel_graph'] =

    context['config_warnings'] = utils.get_configuration_warnings()

    return render(request, 'dashboard/index.html', context)

@staff_member_required
def logs(request):
    level = request.GET.get('level')
    return render(request, 'dashboard/logs.html', {'level': level})

@login_required
def db_logs_modal(request):
    level = request.GET.get('level')

    if level:
        log_list = Log.objects.filter(level=level)
    else:
        log_list = Log.objects.all()
    paginator = Paginator(log_list, LOG_ENTRIES_PER_PAGE) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/logs_excerpt.html', {"logs": logs, "level": level})


@login_required
def app_index(request, app_name):
    '''
    This should query the app for any media related views
    '''
    try:
        app_utils = __import__('project.%s.utils' % app_name)
        return render(request, 'dashboard/app.html', {'assets': app_utils.media()})
    except:
        pass
        # no app builtin mode of retrieving user media

    context = RequestContext(request, {
        'app_name': app_name,
        'assets': {
            'images': get_media('images', app_name),
            'fonts': get_media('fonts', app_name)
        }
    })
    return render(request, 'dashboard/app.html', context)

@login_required
def stat(request, app_name, stat_name):
    '''
    Runs the designated canned query and shows the results
    '''

    from django.utils.importlib import import_module
    try:
        stats = import_module('.stats', app_name)
    except ImportError as err:
        raise Http404

    found = False
    if hasattr(stats, 'SQL_QUERIES'):
        for (name, help_text, sql) in stats.SQL_QUERIES:
            if name == stat_name:
                found = True
                cur = connection.cursor()
                cur.execute(sql)
                data =cur.fetchall()

                colnames = [desc[0] for desc in cur.description]
    if not found:
        raise Http404




    context = RequestContext(request, {
        'app_name': app_name,
        'stat_name': stat_name,
        'help_text': help_text,
        'colnames': colnames,
        'data': data
        })
    return render(request, 'dashboard/stat.html', context)




@login_required
@csrf_exempt
def load_test(request):
    if request.method == 'POST':
        number = request.POST['number']
        if os.environ.get('FLAKY'):
            from random import random
            rnd = random()
            if rnd > 0.8:
                return HttpResponseBadRequest()
            elif rnd > 0.6:
                return HttpResponseForbidden()
            elif rnd > 0.4:
                return HttpResponseNotAllowed()
            elif rnd > 0.2:
                return HttpResponseServerError()
            elif rnd > 0.4 and rnd < 0.6:
                return HttpResponse(json.dumps(dict(number=int(number)*2)))
        return HttpResponse(json.dumps(dict(number=int(number)*2)))

@login_required
def load_test_ui(request):
    return render(request, 'dashboard/load_tester_ui.html')

@login_required
def show_request(request):
    """Lets you inspect details about the request.

    May be useful when investigating web server settings and their effects.
    If you want to temporarily hook it up to handle all patterns, add a URL
    to match everything and route to it.
    """
    params = dict(
            request=request,
            env='\n'.join(['%s=%r' % (k,v) for k,v in os.environ.items()]),
            )
    return render(request, 'dashboard/show_request.html', params)
