from django.conf import settings
from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views


urlpatterns = patterns('',
 
    url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    
    url(r'glsnapshots/$', views.glsnapshots, name='glsnapshots'),
    
    url(r'glsnapshots/balances/(?P<snap_id>[()_a-zA-Z0-9]+)/$', views.glsnapshots_balances),

    url(r'glsnapshots/reconcile/(?P<snap_id>[()_a-zA-Z0-9]+)/(?P<account_id>[()_a-zA-Z0-9]+)$', views.glsnapshots_reconcile),
    url(r'glsnapshots/rechistory/(?P<snap_id>[()_a-zA-Z0-9]+)/(?P<account_id>[()_a-zA-Z0-9]+)$', views.history),

    url(r'glsnapshots/add/$', views.GLSnapshotCreate.as_view(), name="glsnapshot_form"),


    
)
