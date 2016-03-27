from django.conf.urls import *

from accountifie.tasks.views import FinishedTask

import views


urlpatterns = patterns('',
    # report packs
    
    url(r'reporting/get_report/$', views.create_report),
    url(r'reporting/reportsv1/(?P<rpt_id>[_a-zA-Z0-9]+)/$', views.bstrap_report),
    url(r'reporting/api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    
    url(r'reporting/download_ledger/', views.download_ledger),

    # reports
    url(r'reporting/reports/(?P<id>[_a-zA-Z0-9]+)/$', views.report),
    
    # transaction history
    url(r'reporting/history/(?P<type>[()_a-zA-Z0-9]+)/(?P<id>[()_a-zA-Z0-9]+)/$', views.history),
    url(r'reporting/balance_history/(?P<type>[()_a-zA-Z0-9]+)/(?P<id>[()_a-zA-Z0-9]+)/$', views.balance_history),
)

