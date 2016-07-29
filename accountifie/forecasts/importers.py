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


from accountifie.toolkit.forms import FileForm
import accountifie.toolkit
from .models import ProjectionModel, ProjModelv1Param
from accountifie.reporting.models import Metric
from accountifie.gl.models import Account
from accountifie.toolkit.forms import LabelledFileForm

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')



def modelparams_upload(request):
    form = LabelledFileForm(request.POST, request.FILES)
    if form.is_valid():
        label = form.cleaned_data['label']

        upload = request.FILES.values()[0]
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        rslts = process_modelparams(file_name_with_timestamp, label)
        if 'error' in rslts:
            messages.error(request, 'Failed: %s' % rslts['error'])
        else:
            messages.success(request, 'Created %d param entries' % rslts.get('new_count', 0))
            messages.success(request, 'Updated %d para, entries' % rslts.get('updated_count', 0))
            messages.info(request, '%d bad param entries' % rslts.get('bad_count', 0))

        context = {}
        return HttpResponseRedirect('/forecasts')
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the Metrics file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))



def process_modelparams(file_name, label):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    proj_model = ProjectionModel.objects.all().first()
    with open(incoming_name, 'U') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = []
        for row in reader:
            rows.append(row)

    # validation
    if set(headers) != set(['ACCOUNT', 'CONTRA', 'COUNTERPARTY', 'FREQUENCY',
                           'WINDOW', 'METRIC', 'SCALING']):
        return {'error': 'Header columns do not match expected'}

    new_params = 0
    updated_params = 0
    bad_params = 0

    for row in rows:
        d = dict(zip(headers, row))
        # does it exist already?
        # key by ACCOUNT/COUNTERPARTY/LABEL
        p = ProjModelv1Param.objects \
                            .filter(account_id=d['ACCOUNT'],
                                    counterparty_id=d['COUNTERPARTY'],
                                    label=label) \
                            .first()

        metric = Metric.objects \
                       .filter(name=d['METRIC']) \
                       .first()
        if not metric:
            bad_params += 1
            continue

        contra = Account.objects.get(id=d['CONTRA'])
        if p:
            p.frequency = d['FREQUENCY']
            p.window = d['WINDOW']
            p.metric = Metric.objects \
                             .filter(name=d['METRIC']) \
                             .first()
            p.scaling = d['SCALING']
            p.contra = Account.objects.get(id=d['CONTRA'])
            p.save()
            updated_params += 1
        else:
            p_entry = {}
            p_entry['proj_model'] = proj_model
            p_entry['account_id'] = d['ACCOUNT']
            p_entry['contra_id'] = d['CONTRA']
            p_entry['counterparty_id'] = d['COUNTERPARTY']
            p_entry['label'] = label
            p_entry['window'] = d['WINDOW']
            p_entry['scaling'] = d['SCALING']
            p_entry['frequency'] = d['FREQUENCY']
            p_entry['metric'] = metric
            ProjModelv1Param(**p_entry).save()
            new_params += 1

    return {'new_count': new_params,
            'bad_count': bad_params,
            'updated_count': updated_params}
