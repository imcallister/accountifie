from django.conf.urls import patterns, url

from .views import FinishedTask, TaskDetail, task_kill, dashboard_list

urlpatterns = patterns('',
    url(r'^dashboard/$', dashboard_list, name='dashboard_deferreds'),
    url(r'^kill/(?P<tid>\d+)?/$', task_kill, name='task_kill'),
    url(r'^kill/', task_kill, name='task_kill_js'),
    url(r'^complete/$', FinishedTask.as_view(), name='task_complete'),
    url(r'^(?P<pid>\d*)/$', TaskDetail.as_view(), name='task_result'),
    )
