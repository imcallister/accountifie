from django.conf.urls import *

import views


urlpatterns = patterns('', 
    
    # admin-type view

    url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    
    
    (r'^accounts_list/$', views.accounts_list),    
    (r'^transactions/(?P<id>[0-9]+)/$', views.transaction_info),
    
    # utilities
    (r'^get_transactions/', views.download_transactions),
    (r'^get_tranlines/', views.download_tranlines),

)
