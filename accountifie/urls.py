from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'', include('accountifie.toolkit.urls')),
    url(r'', include('accountifie.common.urls')),

    url(r'', include('accountifie.forecasts.urls')),
    url(r'', include('accountifie.gl.urls')),
    url(r'', include('accountifie.snapshot.urls')),
    url(r'', include('accountifie.reporting.urls')),
    url(r'', include('accountifie.environment.urls')),       
)