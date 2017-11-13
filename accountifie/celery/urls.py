from django.conf.urls import url

from . import background_status
from . import views

urlpatterns = [
    url(r'background_task/status/(?P<task_id>[\w\-]+)/$', background_status),
    url(r'tasks/list/$', views.tasks_list),
]
