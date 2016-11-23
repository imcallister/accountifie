from django.conf.urls import url


import views


urlpatterns = [
    url(r'get_report/$', views.create_report),
    url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),
    url(r'upload/(?P<file_type>[_a-zA-Z0-9]+)/$', views.upload_file),
    # reports
    url(r'reports/(?P<id>[_a-zA-Z0-9]+)/$', views.report),
    
    # transaction history
    url(r'history/(?P<type>[()_a-zA-Z0-9]+)/(?P<id>[()_a-zA-Z0-9]+)/$', views.history),
]
