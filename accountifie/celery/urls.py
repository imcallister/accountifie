from django.conf.urls import url

from . import background_status

urlpatterns = [
    url(r'background_task/status/(?P<task_id>[\w\-]+)/$', background_status),
]
