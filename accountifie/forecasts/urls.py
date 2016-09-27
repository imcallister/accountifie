from django.conf.urls import *

from accountifie.tasks.views import FinishedTask

from .views import *

urlpatterns = patterns('',
    url(r'forecasts/get_report/$', create_report),
    url(r'forecasts/run', forecast_run, name='run_forecast'),
    url(r'forecasts/reportpack/finish/$', FinishedTask.as_view(template_name='forecasts/forecast_finish.html'), name="fcast_finished"),
    url(r'forecasts/upload_gl/$', upload_gl, name='upload_gl'),
    url(r'forecasts/forecast/hardcode_projections', hardcode_projections, name="hardcode_projections"),
    url(r'forecasts/forecast/full_projections', all_projections, name="full_projections"),
    url(r'forecasts/reports/(?P<fcast_id>[()_a-zA-Z0-9]+)/(?P<rpt_id>[_a-zA-Z0-9]+)/$', fcast_report, name='fcast_report'),
    url(r'forecasts/forecast/(?P<id>[()_a-zA-Z0-9]+)/$', forecast_detail, name='forecasts_detail'),

    url(r'^forecasts/', forecast_index, name='forecasts_index'),
)
