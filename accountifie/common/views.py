"""
Adapted with permission from ReportLab's DocEngine framework
"""




# Create your views here.
import os, sys
import hashlib
import logging
import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login

from django.contrib.sites.shortcuts import get_current_site

from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError, \
        HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, resolve_url
from django.template import RequestContext, loader
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.http import is_safe_url



from .models import TaskMonitor
from .forms import CommonAuthenticationForm, MultiCommonAuthenticationForm


#currently, this matches our logging config and anything called 'default' goes in the database
#this doesn't sound right but it's a start.
logger = logging.getLogger('default')


# HTTP Error 500
def custom_500(request):
    type, value, tb = sys.exc_info(),

    response = render(request, '500.html', {'message': value})
    response.status_code = 200
    return response


def base_templates(request):
    '''
    To be used as a context_processor so as to provide a fallback if the hosting
    project does not have either base.html or base_site.html templates
    '''
    _docengine_registration = getattr(settings, 'DOCENGINE_REGISTRATION', False)
    _registration_open = getattr(settings, 'REGISTRATION_OPEN', True)
    _USER_PROFILE = getattr(settings, 'REGISTER_USER_PROFILE', getattr(settings,
                                                                       'DOCENGINE_USER_PROFILE',
                                                                      None))
    _base_prefix=''
    if hasattr(request, 'session') and 'subdomain' in request.session:
        if hasattr(settings, 'DOMAINS_PATHS'):
            _base_prefix = dict(settings.DOMAINS_PATHS).get(request.session['subdomain'], '')
        else:
            _base_prefix = request.session['subdomain'] + '/'

    context = {
            'client_project': getattr(settings, 'CLIENT_PROJECT', 'DocEngine'),
            'base_template': loader.select_template([_base_prefix+'base.html', 'base.html', 'common/base.html']),
            'base_site_template': loader.select_template([_base_prefix+'base_site.html', 'base_site.html', 'common/base_site.html']),
            'REGISTRATION_OPEN': _docengine_registration and _registration_open,
            'HAS_PROFILE': isinstance(_USER_PROFILE, str),
            'PROJECT_TITLE': os.path.split(settings.ENVIRON_DIR)[1]
        }

    return context


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='common/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=CommonAuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    if 'accountifie.middleware.ssl.SSLRedirect' not in settings.MIDDLEWARE_CLASSES and\
       'docengine.common.ssl.SecureRequiredMiddleware' not in \
                            settings.MIDDLEWARE_CLASSES and not getattr(settings,
                                                                    'DOCENGINE_HTTPS_SUPPORT',
                                                                        False):

        from django.core.exceptions import ImproperlyConfigured
        msg = 'Authentication is required to run under HTTPS -- Please append\
      "docengine.common.ssl.SSLRedirect" or "docengine.common.ssl.SecureRequiredMiddleware" to MIDDLEWARE_CLASSES in project settings'
        raise ImproperlyConfigured(msg)
    _login_indirect = False
    # the LOGIN_URL refers a absolute URI
    if settings.LOGIN_URL.startswith('http'):
        _login_indirect = True
        _login_server = ('/').join(settings.LOGIN_URL.split('/')[:3])
        if request.get_host() not in settings.LOGIN_URL:
            # get the contents up to the 3rd slash
            return HttpResponseRedirect(_login_server+request.get_full_path())

    if _login_indirect:
        authentication_form = MultiCommonAuthenticationForm

    if request.method == "POST":
        redirect_to = request.POST.get(redirect_field_name, '')

        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            if _login_indirect:
                request.session['subdomain'] = form.cleaned_data['subdomain']
            return HttpResponseRedirect(redirect_to)
    else:
        redirect_to = request.GET.get(redirect_field_name, '')
        request.session.set_test_cookie()
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    if current_app:
        request.current_app = current_app
    return TemplateResponse(request, template_name, context)


def processes(request):
    message = ''
    sortField = 'memory'
    if request.POST:
            kill = request.POST.get('kill', '')
            if kill:
                message = '<p style="color: red;">Process %s was killed. Message returned: %s</p>' % (kill, os.popen('kill %s' % kill).read())
            sortField = request.POST.get('sortField', 'memory')
    processes = []
    fields = 'pid,ppid,user,time,state,%cpu,vsz,command'
    ps = os.popen('ps -o%s -w -w -w -ax | grep python' % fields).read().splitlines()
    ps = [Process(p) for p in ps if p.strip()]

    ppid = str(os.getppid())
    if ppid=='1': parent = pid
    else:
            pid = str(os.getpid())
            p = [p for p in ps if p.pid==pid]
            if p:
                    parent = p[0].ppid

    fields = fields.split(',')
    for p in ps:
            if p.user != 'rptlab' or 'grep' in p.command:
                    continue
            if p.pid==parent:
                    p.color = 'green'
            elif parent!='UNKNOWN' and p.ppid!=parent:
                    continue
            processes.append(p)
    processes = sortByField(processes, sortField)
    params = {'user': request.user,
              'title': 'Diagnose Processes',
              'host': request.META.get('HTTP_HOST', 'Unknown'),
              'processes': processes,
              'parent': parent,
              'message': message,
              'sortField': sortField}
    return render(request, 'common/processes.html', params)

def index(request):
    # Used on first setup, until you define a project-specific one which overrides it
    context = RequestContext(request)
    return render(request, 'common/index.html', context)


def test7491(request):
    # Used by alertra to check servers are working
    delay = request.REQUEST.get('delay', None)
    if delay is not None: time.sleep(float(delay))
    return HttpResponse('I am alive!', content_type='text/plain; charset=utf-8')

@login_required
def deliberateError(*args,**kwds):
    raise ValueError('Deliberately raised error')

class Process(object):

    fields = ['pid', 'ppid', 'user', 'time', 'state', '%cpu', 'vsz', 'command']
    names = [('pid', 'PID'), ('ppid', 'PPID'), ('user', 'User'), ('time', 'Time'), ('state', 'State'), ('%cpu', 'CPU%'), ('vsz', 'Size'), ('command', 'Command')]
    color = 'black'

    def __init__(self, s):
        self.s = s
        s = s.split()
        s[len(self.fields) - 1] = ' '.join(s[len(self.fields) - 1:])
        s = s[:len(self.fields)]
        for i, field in enumerate(self.fields):
            setattr(self, field, s[i].strip().lstrip())
        self.memory = int(self.vsz)
        if self.state == 'Z' or int(self.memory) > 200000:
            self.color = 'red'
        if len(str(self.vsz)) >= 6:
            self.vsz = '%sM' % str(self.memory / 1024)
        else:
            self.vsz = '%sK' % self.vsz

    def __unicode__(self):
        return force_unicode(self.s)

def sortByField(l, field):
    def fieldSort(a, b):
        if getattr(a, field, '') > getattr(b, field, ''): return 1
        if getattr(a, field, '') == getattr(b, field, ''): return 0
        return -1
    l.sort(fieldSort)
    return l

def media_types(app_name=''):
    '''
    Lists folders in media directory
    Takes optional app_name for which user folder to look into

    '''
    media_path = os.path.join(setting.MEDIA_ROOT, app_name)
    try:
        return [entry for entry in os.listdir(media_path) if os.path.isdir(os.path.join(media_path, entry)) ]
    except OSError:
        raise True("%s does not exist or it is not a folder" % media_path)


def media(media_type, app_name=''):
    '''
    Returns the list of [user] media items
    Takes optional app_name for which user folder to look into
    media_type = [ image | font | pallete | style | ... ]
    '''
    if media_type in media_type(app_name):
        media_path = os.path.join(settings.MEDIA_ROOT, app_name, media_type)
        if os.path.isdir(os.path.join(media_path)):
            return os.listdir(media_path)
    #no such media type
    return []


@login_required
def upload(request):
    "Handles user file uploads into a queue"

    result = {'success': False}
    if request.method == 'POST':
        if not os.path.isdir(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)

        if len(request.FILES) == 1:
            upload = list(request.FILES.values())[0]
            rawdata = upload.read()
            result['bytes_received'] = len(rawdata)

            hasher = hashlib.md5()
            hasher.update(rawdata)
            ident = hasher.hexdigest()[0:6]

            info = {
                'filename': upload.name,
                'user': request.user.username,
                'remote_addr': request.META['REMOTE_ADDR']
                }
            datafilename = os.path.join(settings.UPLOAD_DIR, '%s.dat' % ident)
            infofilename = os.path.join(settings.UPLOAD_DIR, '%s.inf' % ident)
            open(datafilename, 'wb').write(rawdata)
            open(infofilename, 'wb').write(json.dumps(info))

            result['success'] = True
            result['message'] = 'File saved as "%s.dat"' % ident
            result['id'] = ident

            logger.info('User %s uploaded file %s, saved as %s' % (request.user, datafilename, ident))

            return HttpResponse(json.dumps(result), content_type='application/javascript; charset=utf8')
    else:
        result['message'] = 'You need to do a POST request to upload anything'
    return HttpResponse(json.dumps(result))


def server_error(request, template_name='500.html'):
    # like django.views.defaults.server_error, but uses RequestContext
    t = loader.select_template([template_name, 'common/500.html'])
    try:
        request_context = RequestContext(request, {})
    except:
        request_context = {}
    # will allow raising an exception if tempalte can't be rendered
    response = t.render(request_context)
    return HttpResponseServerError(response)


def not_found(request, template_name='404.html'):
    # like django.views.defaults.server_error, but uses RequestContext
    t = loader.select_template([template_name, 'common/404.html'])
    try:
        request_context = RequestContext(request, {})
    except:
        request_context = {}
    # will allow raising an exception if tempalte can't be rendered
    response = t.render(request_context)
    return HttpResponseNotFound(response)


@login_required
def check_all_tasks(request):
    '''endpoint to check up on tasks that are either still running
    or that have finished and were started less then 5 min ago'''
    tasks = []
    now = datetime.now()
    five_min = timedelta(seconds=300)
    past = now - five_min
    monitors = TaskMonitor.objects.filter(Q(creation_timestamp__gte=past) | Q(task_state='started'))
    for m in monitors:
        tasks.append(dict(task_id=m.task_id,
                          task_name=m.task_name,
                          traceback=m.traceback,
                          task_state=m.task_state,
                          percent_complete=m.percent_complete,
                          timestamp=m.creation_timestamp.strftime("%A, %d. %B %Y %I:%M%p"),
                          )
                     )
    return HttpResponse(json.dumps(tasks))
