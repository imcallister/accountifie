from django.conf import settings
from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views


urlpatterns = patterns('',
 
    url(r'snapshot/glsnapshots/$', views.glsnapshots, name='glsnapshots'),
    url(r'snapshot/glsnapshots/balances/(?P<snap_id>[()_a-zA-Z0-9]+)/$', views.glsnapshots_balances),
    #url(r'snapshot/glsnapshots/reconcile/(?P<snap_id>[()_a-zA-Z0-9]+)/(?P<account_id>[()_a-zA-Z0-9]+)$', views.glsnapshots_reconcile),
    #url(r'snapshot/glsnapshots/rechistory/(?P<snap_id>[()_a-zA-Z0-9]+)/(?P<account_id>[()_a-zA-Z0-9]+)$', views.history),
    
)
