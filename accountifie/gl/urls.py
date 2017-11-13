from django.conf.urls import *

from . import views
from . import jobs


urlpatterns = [

    # admin-type view
    url(r'gl/accounts_list/$', views.accounts_list),
    url(r'gl/counterparty_list/$', views.counterparty_list),

    # utilities
    url(r'gl/get_transactions/', views.download_transactions),
    url(r'gl/get_tranlines/', views.download_tranlines),

    url(r'celery/recalculate/', jobs.recalculate),
]
