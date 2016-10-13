import logging
import pandas as pd
import datetime
import json
import operator
import csv
import os
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.utils.html import mark_safe
from django.views.generic.edit import CreateView, DeleteView
from django.conf import settings

import djcelery.models

from .models import Forecast
from .forms import ForecastForm
import apiv1 as fcst_api
from accountifie.query.query_manager import QueryManager
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils
from accountifie.common.table import get_table
from accountifie.toolkit.forms import LabelledFileForm, FileForm


logger = logging.getLogger('default')


@login_required
def forecast_index(request):
    context = {}
    context['title'] = 'Forecasts'
    context['content'] = get_table('forecasts')()
    return render(request, 'forecasts/forecast_list.html', context)


@login_required
def forecasts_reports(request):
    fcast_choices = [(f.id, f.label) for f in Forecast.objects.all()]
    context = {}
    context['fcasts'] = fcast_choices
    return render(request, 'forecasts/forecast_reports.html', context)


@login_required
def upload_gl(request):
    if request.method != "POST":
        forecast_obj = Forecast.objects.get(id=request.GET.get('forecast'))
        context = {'file_category': 'GL Projections'}
        context['file_type'] = '.csv'
        context['obj_label'] = forecast_obj.label
        form = FileForm()
        context['form'] = form

        return render(request, 'forecasts/upload_gl.html', context)
    else:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            upload = io.StringIO(unicode(request.FILES.values()[0].read()), newline=None)
            data = [row for row in csv.DictReader(upload)]
            forecast_obj = Forecast.objects.get(id=request.GET.get('forecast'))
            forecast_obj.hardcode_projections = data
            forecast_obj.save()
            return HttpResponseRedirect('/forecasts/forecast/%s' % forecast_obj.id)


def _order_projections(projs):
    cols = [x for x in projs[0].keys() if x not in ['Debit','Credit','Counterparty','Company']]

    def _idxer(label):
        lbls = label.split('M')
        yr = int(lbls[0])
        mth = int(lbls[1])
        return 2015 * yr + mth

    col_indexer = dict((x, _idxer(x)) for x in cols)
    return [x[0] for x in sorted(col_indexer.items(), key=operator.itemgetter(1))]


@login_required
def hardcode_projections(request):
    fcast_id = request.GET.get('fcast_id')
    hcode_projs = fcst_api.hardcode_projections(fcast_id, {})
    if len(hcode_projs) > 0:
        col_order = _order_projections(hcode_projs)
        context = {'cols': zip(['Debit', 'Credit', 'Counterparty', 'Company'] + col_order, ['nameFormatter']*4 + ['valueFormatter'] * len(col_order))}
        context['data_url'] = '/api/forecasts/hardcode_projections/%s?raw=true' % fcast_id
    else:
        context = {}
    return render(request, 'forecasts/bstrap_report.html', context)


@login_required
def all_projections(request):
    fcast_id = request.GET.get('fcast_id')
    projs = fcst_api.all_projections(fcast_id, {})
    if len(projs) > 0:
        col_order = _order_projections(projs)
        context = {'cols': zip(['Debit', 'Credit', 'Counterparty', 'Company'] + col_order, ['nameFormatter']*4 + ['valueFormatter'] * len(col_order))}
        context['data_url'] = '/api/forecasts/all_projections/%s?raw=true' % fcast_id
    else:
        context = {}

    return render(request, 'forecasts/bstrap_report.html', context)

def report_prep(request, id, version=None, strategy=None):

    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)

    format = request.GET.get('format', 'html')
    company_id = request.GET.get('company', utils.get_company(request))
    path = request.GET.get('path', None)
    report = accountifie.reporting.rptutils.get_report(id, company_id, version=version)

    if (company_id not in report.works_for):
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render(request, '404.html', {'message': msg}), False

    report.configure(as_of=as_of, col_tag=col_tag, path=path)

    report.set_gl_strategy(strategy)
    return report, True, format


def create_report(request):

    fcast_id = request.GET.get('fcast_id')

    if 'date' in request.GET:
        dt = request.GET.get('date')
        rpt = request.GET.get('rpt')
        url = '/forecasts/reports/%s/%s?date=%s' % (fcast_id, rpt, dt)
    elif 'mth' in request.GET:
        mth = request.GET.get('mth')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/forecasts/reports/%s/%s?col_tag=%sM%s' % (fcast_id, rpt, yr, mth)
    elif 'qtr' in request.GET:
        qtr = request.GET.get('qtr')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/forecasts/reports/%s/%s?col_tag=%sQ%s' % (fcast_id, rpt, yr, qtr)    
    else:
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        period = request.GET.get('period')
        url = '/forecasts/reports/%s/%s?col_tag=%s%s' % (fcast_id, rpt, yr, period)    

    clear_cache = request.GET.get('cl_cache', None)
    if clear_cache:
        if clear_cache == 'checked':
            url += '&clear_cache=True'

    return HttpResponseRedirect(url)


def fcast_report(request, fcast_id, rpt_id):

    fcast = Forecast.objects.get(id=fcast_id)

    strategy = QueryManagerStrategyFactory().get('forecast')
    strategy.set_cache(fcast_id=fcast_id, proj_gl_entries=fcast.get_gl_entries())

    report, is_report, format = report_prep(request, rpt_id, version='v1', strategy=strategy)
    if not is_report:
        return report

    report_data = report.calcs()
    
    if format == 'json':
        return HttpResponse(json.dumps(report_data, cls=DjangoJSONEncoder), content_type="application/json")
    elif format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x == '' else str(x['text'])
        for row in report_data:
            writer.writerow([row['label']] + [map_values(row[col]) for col in [x for x in report.column_order if x in row]])
        return response
    elif format == 'html':
        # not bootstrap ... the more custom style for more complex reports
        context = report.html_report_context()
        context['query_string'] = request.META['QUERY_STRING']
        context['rows'] = []
        for rec in report_data:
            context['rows'] += report.get_row(rec)

        return render(request, 'report.html', context)
    else:
        msg = "Sorry. This format is not recognised : %s" % format
        return render(request, '404.html', {'message': msg}), False


@login_required
def forecast_detail(request, id):
    try:
        forecast = Forecast.objects.get(id=id)
    except Forecast.DoesNotExist:
        raise Http404

    form = ForecastForm(instance=forecast)

    context = dict(
        f=forecast,
        form=form
        )
    return render(request, 'forecasts/forecast_detail.html', context)



