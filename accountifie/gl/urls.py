from django.conf.urls import *

import views
import jobs


urlpatterns = [

    url(r'^counterparty-autocomplete/$',
         views.CounterpartyAutocomplete.as_view(),
         name='counterparty-autocomplete',
    ),
 
    url(r'^account-autocomplete/$',
         views.AccountAutocomplete.as_view(),
         name='account-autocomplete',
    ),

    # admin-type view
    url(r'gl/accounts_list/$', views.accounts_list),
    url(r'gl/counterparty_list/$', views.counterparty_list),

    # utilities
    url(r'gl/get_transactions/', views.download_transactions),
    url(r'gl/get_tranlines/', views.download_tranlines),

    url(r'celery/recalculate/', jobs.recalculate),
]
