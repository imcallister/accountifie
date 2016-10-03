from django.conf import settings
from django.conf.urls import include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views


urlpatterns = [
    url(r'snapshot/glsnapshots/$', views.glsnapshots, name='glsnapshots'),
    url(r'snapshot/glsnapshots/balances/(?P<snap_id>[()_a-zA-Z0-9]+)/$', views.glsnapshots_balances),   
]
