from django.conf.urls import *

import views


urlpatterns = patterns('', 

    url(r'^counterparty-autocomplete/$',
        views.CounterpartyAutocomplete.as_view(),
        name='counterparty-autocomplete',
    ),

    url(r'^account-autocomplete/$',
        views.AccountAutocomplete.as_view(),
        name='account-autocomplete',
    ),

    # admin-type view
    (r'gl/accounts_list/$', views.accounts_list),
    (r'gl/counterparty_list/$', views.counterparty_list),

    # utilities
    (r'gl/get_transactions/', views.download_transactions),
    (r'gl/get_tranlines/', views.download_tranlines),

)
