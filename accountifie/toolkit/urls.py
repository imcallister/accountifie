from django.conf import settings
from django.conf.urls import url, static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
import accountifie.tasks.views
import django.views.static

urlpatterns = [
    url(r'^choose_company/(?P<company_id>.*)/$', views.choose_company, name='choose_company'),    
    url(r'^upload/complete/$', accountifie.tasks.views.FinishedTask.as_view(), name='upload_complete'),
    url(r'^cleanlogs/$', views.cleanlogs, name='cleanlogs'),
    url(r'^recalculate/$', views.recalculate, name='recalculate'),
    url(r'^primecache/$', views.primecache, name='primecache'),
    url(r'^dump_fixtures/$', views.dump_fixtures),
]    


"""
if settings.DEVELOP:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



    urlpatterns += staticfiles_urlpatterns()
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        })
    )

    urlpatterns.append(
        url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.DATA_ROOT,
        })
    )
    """
