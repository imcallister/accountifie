from django.conf import settings
from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from . import api

urlpatterns = patterns('',
 
    url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),

)

#handler404 = views.error404
