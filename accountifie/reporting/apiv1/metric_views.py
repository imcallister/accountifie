from multipledispatch import dispatch

from django.db.models import Prefetch

from accountifie.reporting.models import *
from accountifie.reporting.serializers import *


def metric_labels(qstring):
    labels = MetricEntry.objects.all().values('label').distinct()
    return [x['label'] for x in labels if x['label'] not in [None, '']]


@dispatch(dict)
def metric(qstring):
    label = qstring.get('label', None)
    if type(label) == list:
        label = label[0]
    if label:
        qs = MetricEntry.objects.filter(label=label)
        return MetricEntrySerializer(qs, many=True).data
    else:
        return None


@dispatch(str, dict)
def metric(name, qstring):
    label = qstring.get('label', None)
    if type(label) == list:
        label = label[0]
    if label:
        qs = MetricEntry.objects.filter(metric__name=name) \
                                .filter(label=label)

        return MetricEntrySerializer(qs, many=True).data
    else:
        return None
