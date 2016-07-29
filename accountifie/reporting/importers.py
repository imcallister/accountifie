import os
import csv
import datetime
from dateutil.parser import parse
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect


from accountifie.toolkit.forms import LabelledFileForm
import accountifie.toolkit
from .models import Metric, MetricEntry

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')



def order_upload(request):
    form = LabelledFileForm(request.POST, request.FILES)

    if form.is_valid():
        label = form.cleaned_data['label']

        upload = request.FILES.values()[0]
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        rslts = process_metrics(file_name_with_timestamp, label)
        if 'error' in rslts:
            messages.error(request, 'Failed: %s' % rslts['error'])
        else:
            messages.success(request, 'Created %d metric entries' % rslts.get('new_count', 0))
            messages.success(request, 'Updated %d metric entries' % rslts.get('updated_count', 0))
            messages.info(request, '%d new metrics' % rslts.get('new_metrics', 0))

        context = {}
        return HttpResponseRedirect('/forecasts')
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the Metrics file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_metrics(file_name, label):
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

    return {'new_count': new_entry_cnt,
            'new_metrics': new_metrics,
            'updated_count': update_entry_cnt}
