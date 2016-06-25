from django.conf import settings
from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from . import uploader
import accountifie.tasks.views

urlpatterns = patterns('',
    
    url(r'^choose_company/(?P<company_id>.*)/$', views.choose_company, name='choose_company'),    
    url(r'^upload/complete/$', accountifie.tasks.views.FinishedTask.as_view(), name='upload_complete'),
    url(r'^cleanlogs/$', views.cleanlogs, name='cleanlogs'),
    url(r'^recalculate/$', views.recalculate, name='recalculate'),
    url(r'^primecache/$', views.primecache, name='primecache'),
    url(r'^dump_fixtures/$', views.dump_fixtures),
    

)

if settings.DEVELOP:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    urlpatterns += patterns('',
        url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.DATA_ROOT,
        }),
    )
