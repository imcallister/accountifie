from django.conf.urls import *
#from django.views.generic import ListView

from accountifie.tasks.views import FinishedTask

#from .models import Forecast
from .views import *
#from . import views



urlpatterns = patterns('',
	
    #url(r'forecasts/reports_center/$', forecasts_reports, name='forecasts_reports'),
    url(r'forecasts/get_report/$', create_report),
    
    #url(r'add/$', ForecastCreate.as_view(), name="forecasts_form"),
    url(r'forecasts/delete/(?P<pk>[()_a-zA-Z0-9]+)/$', ForecastDelete.as_view(), name="forecast_delete"),
    
    url(r'forecasts/run/$', forecast_run, name='run_forecast'),
    url(r'forecasts/reportpack/finish/$', FinishedTask.as_view(template_name='forecasts/forecast_finish.html'), name="fcast_finished"),
    url(r'forecasts/upload_gl/$', upload_gl, name='upload_gl'),

    url(r'forecasts/forecast/projections',  gl_projections, name="fcast_projections"),
    url(r'forecasts/reports/(?P<fcast_id>[()_a-zA-Z0-9]+)/(?P<rpt_id>[_a-zA-Z0-9]+)/$', fcast_report, name='fcast_report'),
    url(r'forecasts/forecast/(?P<id>[()_a-zA-Z0-9]+)/$', forecast_detail, name='forecasts_detail'),

    url(r'forecasts/', forecast_index, name='forecasts_index'),
 
)