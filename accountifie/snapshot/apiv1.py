from multipledispatch import dispatch

from django.forms import model_to_dict

from accountifie.snapshot.models import GLSnapshot
from accountifie.common.api import api_wrapper
import logging

logger = logging.getLogger('default')



@dispatch(dict)
def glsnapshot(qstring):
    return list(GLSnapshot.objects.order_by('id').values())


@dispatch(str, dict)
def glsnapshot(snap_id, qstring):
    return model_to_dict(GLSnapshot.objects.get(id=snap_id))
