from django.conf.urls import url

import views
import jobs


urlpatterns = [
    url(r'forecasts/run', jobs.run_forecast, name='run_forecast'),

    url(r'forecasts/upload_gl/$', views.upload_gl, name='upload_gl'),
    url(r'forecasts/forecast/hardcode_projections', views.hardcode_projections, name="hardcode_projections"),
    url(r'forecasts/forecast/full_projections', views.all_projections, name="full_projections"),
    url(r'forecasts/reports/(?P<fcast_id>[()_a-zA-Z0-9]+)/(?P<rpt_id>[_a-zA-Z0-9]+)/$', views.fcast_report, name='fcast_report'),
    url(r'forecasts/forecast/(?P<id>[()_a-zA-Z0-9]+)/$', views.forecast_detail, name='forecasts_detail'),
    url(r'^forecasts/index/', views.forecast_index, name='forecasts_index'),
]
