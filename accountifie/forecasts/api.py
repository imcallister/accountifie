import json

from .models import Forecast


def get_fld(record, fld):
    return getattr(record, fld)

def get_record_data(record, flds):
    data = dict((fld, get_fld(record, fld)) for fld in flds)
    return data


def forecasts_list():
    records = Forecast.objects.all()
    flds = ['id_link', 'label', 'start_date', 'comment']
    return [get_record_data(rec, flds) for rec in records]


def projections(fcast_id):
    data = Forecast.objects.get(id=fcast_id).projections
    return data
