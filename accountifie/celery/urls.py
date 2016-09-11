from django.conf.urls import patterns, url

from . import background_status

urlpatterns = patterns('',
    url(r'background_task/status/(?P<task_id>[\w\-]+)/$', background_status),
    )
