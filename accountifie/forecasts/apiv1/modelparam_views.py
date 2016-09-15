
from accountifie.forecasts.models import *
from accountifie.forecasts.serializers import *


def projmodelv1param(label, qstring):
    if label:
        qs = ProjModelv1Param.objects.filter(label=label)
        return ProjModelv1ParamSerializer(qs, many=True).data
    else:
        return None
