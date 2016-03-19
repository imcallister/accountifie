from django.conf.urls import *

from accountifie.tasks.views import FinishedTask

import views


urlpatterns = patterns('',
    # report packs
    
    url(r'reporting/get_report/$', views.create_report),
    url(r'reporting/reportsv1/(?P<rpt_id>[_a-zA-Z0-9]+)/$', views.bstrap_report),
    url(r'reporting/api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    
    (r'reporting/download_ledger/', views.download_ledger),

    # reports
    (r'reporting/reports/(?P<id>[_a-zA-Z0-9]+)/$', views.report),
    
    # transaction history
    (r'reporting/history/(?P<type>[()_a-zA-Z0-9]+)/(?P<id>[()_a-zA-Z0-9]+)/$', views.history),
    (r'reporting/balance_history/(?P<type>[()_a-zA-Z0-9]+)/(?P<id>[()_a-zA-Z0-9]+)/$', views.balance_history),
)

