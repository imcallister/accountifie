from multipledispatch import dispatch


from accountifie.forecasts.models import Forecast
from accountifie.forecasts.serializers import ForecastSerializer
import logging

logger = logging.getLogger('default')


@dispatch(dict)
def forecast(qstring):
    qs = Forecast.objects.all().order_by('-start_date')
    return list(ForecastSerializer(qs, many=True).data)


@dispatch(str, dict)
def forecast(label,qstring):
    qs = Forecast.objects.filter(label=label).first()
    return ForecastSerializer(qs).data


def hardcode_projections(fcast_id, qstring):
    return Forecast.objects.get(id=fcast_id).hardcode_projections


def all_projections(fcast_id, qstring):
    return Forecast.objects.get(id=fcast_id).get_projections()
