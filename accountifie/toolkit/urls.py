from django.conf import settings
from django.conf.urls import url, static

from . import views
from . import jobs


urlpatterns = [
    url(r'^choose_company/(?P<company_id>.*)/$', views.choose_company, name='choose_company'),    
    url(r'^cleanlogs/$', jobs.cleanlogs, name='cleanlogs'),
    url(r'^primecache/$', jobs.primecache, name='primecache'),
    url(r'^dump_fixtures/$', views.dump_fixtures),
]    

