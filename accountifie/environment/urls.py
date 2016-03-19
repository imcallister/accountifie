from django.conf import settings
from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from . import api

urlpatterns = patterns('',
 
    url(r'environment/api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),

    url(r'api/environment/(?P<api_view>[_a-zA-Z0-9]+)/(?P<variable>[_a-zA-Z0-9]+)/$', views.new_api),

)