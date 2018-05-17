from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [

    #url(r'^admin/', include(admin.site.urls)),

    url(r'', include('accountifie.toolkit.urls')),
    url(r'', include('accountifie.common.urls')),
    url(r'', include('accountifie.celery.urls')),
    url(r'', include('accountifie.gl.urls')),

]
