from multipledispatch import dispatch

from django.forms import model_to_dict

from accountifie.forecasts.models import Forecast
from accountifie.common.api import api_wrapper
import logging

logger = logging.getLogger('default')



def get_fld(record, fld):
    return getattr(record, fld)

def get_record_data(record, flds):
    data = dict((fld, get_fld(record, fld)) for fld in flds)
    return data

@dispatch(dict)
def forecast(qstring):
    records = Forecast.objects.all()
    flds = ['id_link', 'label', 'start_date', 'comment']
    return [get_record_data(rec, flds) for rec in records]


@dispatch(str, dict)
def forecast(label,qstring):
    rec = Forecast.objects.get(label=label)
    flds = ['id_link', 'label', 'start_date', 'comment']
    return get_record_data(rec, flds)

def projections(fcast_id, qstring):
    data = Forecast.objects.get(id=fcast_id).projections
    return data
