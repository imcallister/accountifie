import os, signal, time, json, sys
from ast import literal_eval

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect,\
        HttpResponseNotFound
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse

from .models import DeferredTask
from .utils import utcnow, timedelta, pid2cmdline, initialCmdStr


@login_required
def dashboard_list(request):
    someTimeAgo = utcnow() - timedelta(seconds=getattr(settings,'DOCENGINE_TASKS_RECENT_SECONDS',24*3600))
    dtasks = list(DeferredTask.objects.filter(Q(start__gt=someTimeAgo)|Q(finished=False)).order_by('finished','-start'))
    return render(request, 'dashboard/dashboard_deferreds.html', {"dtasks": dtasks})


@staff_member_required
def task_kill(request,tid):
    tid = int(tid)
    try:
        dtask = DeferredTask.objects.get(id=tid)
    except DeferredTask.DoesNotExist:
        raise Http404('No dtask with id=%d' % id)
    pid = dtask.pid
    cmdline = pid2cmdline(pid)
    if cmdline.startswith(initialCmdStr(dtask.task)):
        try:
            os.kill(pid,signal.SIGQUIT)
            finish = utcnow()
            n = 10
            while n and pid2cmdline(pid):
                time.sleep(1)
                n -= 1
            dtask.finished = True
            dtask.success = False
            dtask.finish = finish
            dtask.status = 'killed'
            dtask.save()
            return HttpResponse('OK',content_type='text/plain')
        except:
            return HttpResponseNotFound('FAILED',content_type='text/plain')
    raise Http404('invalid command line\n%s\nfor task id=%d with pid=%d' %(cmdline,tid,pid))


class FinishedTask(DetailView):
    '''A generic view which allows `template_name` to be passed in the url
    pattern so as to deliver the propper interface for each project
    '''

    model = DeferredTask
    template_name = 'tasks/task_report.html'

    def get_object(self, queryset=None):
        '''gets the pid from the querystring param p
        '''
        if getattr(self, 'object', None):
            return self.object
        pid = self.request.GET.get('pid', False)
        if not pid:
            return super(FinishedTask, self).get_object(queryset)
        try:
            obj = self.get_queryset().filter(pid=pid).latest('start')
        except DeferredTask.DoesNotExist:
            obj = None
        return obj

    def get_context_data(self, **kwargs):
        '''deserialise results
        '''
        context_data = super(FinishedTask, self).get_context_data(**kwargs)
        obj = self.get_object()
        finished = getattr(obj, 'finished', False)
        if finished:
            try:
                context_data['results'] = json.loads(obj.stdout)
            except:
                context_data['results'] = obj.stdout.split('\n')
        if getattr(obj, 'kwds', {}):
            #kwds = json.loads(obj.kwds)
            context_data['kwds'] = literal_eval(obj.kwds)
            
        return context_data


class TaskDetail(FinishedTask):
    """Shows task-in-progress
    Users should override `template_name` in the url pattern if they which to
    deliver their own custom interface.
    """
    template_name = 'tasks/task_status.html'

    def get_object(self, queryset=None):
        if getattr(self, 'object', None):
            return self.object
        if queryset is None:
            queryset = self.get_queryset()
        pid = int(self.kwargs.get('pid', '0'))
        if pid == 0:
            return super(TaskDetail, self).get_object(queryset)

        # we might have records with same PID
        try:
            obj = queryset.filter(pid=pid).latest('start')
        except DeferredTask.DoesNotExist:
            obj = None
        return obj

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if getattr(self.object, 'finished', False):
            success_url = getattr(self.object, 'success_url', '')
            if success_url in ['',None]:
               success_url = '%s?pid=%s' % (reverse('task_complete'), self.kwargs.get('pid',0))
            if success_url not in ['',None]:
                return HttpResponseRedirect(success_url)
        return super(TaskDetail, self).get(*args, **kwargs)
