from django.conf import settings
from django.conf.urls import url, static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from . import uploader
from . import jobs
import accountifie.tasks.views
import django.views.static

urlpatterns = [
    url(r'^choose_company/(?P<company_id>.*)/$', views.choose_company, name='choose_company'),    
    url(r'^upload/complete/$', accountifie.tasks.views.FinishedTask.as_view(), name='upload_complete'),
    url(r'^cleanlogs/$', jobs.cleanlogs, name='cleanlogs'),
    url(r'^primecache/$', jobs.primecache, name='primecache'),
    url(r'^dump_fixtures/$', views.dump_fixtures),
]    

