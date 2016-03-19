from django.conf.urls import *

import views


urlpatterns = patterns('', 
    
    # admin-type view

    url(r'gl/api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    
    
    (r'gl/accounts_list/$', views.accounts_list),    
    (r'gl/counterparty_list/$', views.counterparty_list),    
    (r'gl/transactions/(?P<id>[0-9]+)/$', views.transaction_info),
    
    # utilities
    (r'gl/get_transactions/', views.download_transactions),
    (r'gl/get_tranlines/', views.download_tranlines),

)
