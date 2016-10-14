import os
import csv
import datetime
from dateutil.parser import parse
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect


from accountifie.toolkit.forms import LabelledFileForm
from accountifie.common.uploaders.csv import save_file
from .models import Metric, MetricEntry

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def process_metrics(file_name, label=None):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = []
        for row in reader:
            rows.append(row)

    # validation

    new_metrics = 0
    metric_objs = {}
    if header[0] != 'DATE':
        return {'error': 'First column must be DATE'}

    for col in header[1:]:
        metric_obj = Metric.objects.filter(name=col).first()
        if not metric_obj:
            metric_obj = Metric(name=col)
            metric_obj.save()
            new_metrics += 1
        metric_objs[col] = metric_obj

    as_of = datetime.datetime.now().date()
    new_entry_cnt = 0
    update_entry_cnt = 0

    for row in rows:

        try:
            dt = parse(row[0])
        except:
            return {'error': 'Bad DATE: %s' % row[0]}
        for col_num in range(1, len(header)):
            try:
                value = Decimal(row[col_num])
                col = header[col_num]
                m_entry = {}
                m_entry['metric'] = metric_objs[col]
                m_entry['date'] = dt
                m_entry['balance'] = Decimal(row[col_num])
                m_entry['label'] = label
                m_entry['as_of'] = as_of
                obj = MetricEntry.objects \
                                 .filter(metric=m_entry['metric'],
                                         date=dt,
                                         label=label) \
                                 .first()
                if obj:
                    obj.balance = Decimal(row[col_num])
                    obj.as_of = as_of
                    update_entry_cnt += 1
                else:
                    MetricEntry(**m_entry).save()
                    new_entry_cnt += 1
            except:
                pass

    msg_list = []
    msg_list.append('Created %d metric entries' % new_entry_cnt)
    msg_list.append('Updated %d metric entries' % new_metrics)
    msg_list.append('%d new metrics' % update_entry_cnt)
    return msg_list, []
