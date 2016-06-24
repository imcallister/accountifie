from multipledispatch import dispatch

from django.forms import model_to_dict

from accountifie.snapshot.models import GLSnapshot
from accountifie.common.api import api_wrapper
import logging

logger = logging.getLogger('default')

def get_fld(record, fld):
    return getattr(record, fld)

def get_record_data(record, flds):
    data = dict((fld, get_fld(record, fld)) for fld in flds)
    return data



@dispatch(dict)
def glsnapshot(qstring):
    records = GLSnapshot.objects.order_by('id')
    flds = ['id', 'desc_link','short_desc', 'snapped_at', 'closing_date', 'comment']
    return [get_record_data(rec, flds) for rec in records]


@dispatch(str, dict)
def glsnapshot(snap_id, qstring):
    return model_to_dict(GLSnapshot.objects.get(id=snap_id))
