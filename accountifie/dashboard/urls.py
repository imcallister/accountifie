"""
Adapted with permission from ReportLab's DocEngine framework
"""


from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^logs_data/$', db_logs_modal, name='dashboard_logs'),
    url(r'^logs/$', logs, name='logs'),
    url(r'^load_test/$', load_test, name='load_test'),
    url(r'^show_request/$', show_request, name='show_request'),
    url(r'^load_test_ui/$', load_test_ui, name='load_test_ui'),
    url(r'^stats/(?P<app_name>[0-9a-zA-Z_\.]+)/(?P<stat_name>\w+)/$', stat, name='dashboard_stat'),
    url(r'^(\w+)/$', app_index, name='dashboard_app'),
    url(r'^$', index, name="dashboard_index"),
]    
