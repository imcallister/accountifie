import logging
import pandas as pd
import datetime
import json
import operator
import csv
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.html import mark_safe
from django.views.generic.edit import CreateView, DeleteView
from django.conf import settings

from forms import FileForm

from accountifie.tasks.utils import task

from .models import Forecast
from .forms import ForecastBetterForm, ForecastForm
from .importers import modelparams_upload
import accountifie.forecasts.api
from accountifie.query.query_manager import QueryManager
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils
from accountifie.common.table import get_table
from accountifie.toolkit.forms import LabelledFileForm



logger = logging.getLogger('default')


def api(request, api_view):
    return globals()[api_view](request)


@login_required
def forecasts_list(request):
    return HttpResponse(json.dumps(accountifie.forecasts.api.forecasts_list(), cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def forecast_index(request):
    context = {}
    context['title'] = 'Forecasts'
    context['content'] = get_table('forecasts')()
    return render_to_response('forecasts/base_forecasts.html', context, context_instance=RequestContext(request))


"""
class ForecastCreate(CreateView):

    model = Forecast
    form_class = ForecastBetterForm
    template_name = 'forecasts/forecast_form.html'
    success_url = reverse_lazy('forecasts_index')
"""

class ForecastDelete(DeleteView):

    model = Forecast
    success_url = reverse_lazy('forecasts_index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.info(request, 'Successfully deleted forecast %s' % \
                      self.object.id)
        return HttpResponseRedirect(success_url)


@login_required
def forecasts_reports(request):
    fcast_choices = [(f.id, f.label) for f in Forecast.objects.all()]
    context = {}
    context['fcasts'] = fcast_choices
    return render_to_response('forecasts/forecast_reports.html', context, RequestContext(request))


@login_required
def upload_file(request, file_type, check=False):

    if request.method == 'POST':
        if file_type == 'modelparams':
            return modelparams_upload(request)
        else:
            raise ValueError("Unexpected file type; know about metrics")
    else:
        form = LabelledFileForm()
        context = {'form': form, 'file_type': file_type}
        return render_to_response('common/upload_csv.html',
                                  context,
                                  context_instance=RequestContext(request))


@login_required
def upload_gl(request):
    if request.method != "POST":
        forecast_obj = Forecast.objects.get(id=request.GET.get('forecast'))
        context = {'file_category': 'GL Projections'}
        context['file_type'] = '.json'
        context['obj_label'] = forecast_obj.label
        form = FileForm()
        context['form'] = form

        return render_to_response('forecasts/upload_gl.html', RequestContext(request, context))
    else:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            upload = request.FILES.values()[0]
            file_name = upload._name
            data = json.loads(upload.file.read())
            forecast_obj = Forecast.objects.get(id=request.GET.get('forecast'))
            forecast_obj.projections = data
            forecast_obj.save()
            return HttpResponseRedirect('/forecasts/forecast/%s' % forecast_obj.id)
        

@login_required
def gl_projections(request):
    fcast_id = request.GET.get('fcast_id')
    fcast = Forecast.objects.get(id=fcast_id)

    cols = [x for x in fcast.projections[0].keys() if x not in ['Debit','Credit','Counterparty','Company']]

    def idxer(label):
        lbls = label.split('M')
        yr = int(lbls[0])
        mth = int(lbls[1])
        return 2015 * yr + mth

    col_indexer = dict((x, idxer(x)) for x in cols)
    col_order = [x[0] for x in sorted(col_indexer.items(), key=operator.itemgetter(1))]

    context = {'cols': zip(['Debit','Credit','Counterparty','Company'] + col_order, ['nameFormatter']*4 + ['valueFormatter'] * len(col_order))}

    context['data_url'] = '/api/forecasts/projections/%s/' % fcast_id

    return render_to_response('forecasts/bstrap_report.html', context, 
          context_instance = RequestContext(request)
          )

def get_gl_projections(request, fcast_id):
    data = accountifie.forecasts.api.projections(fcast_id)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json")

def report_prep(request, id, version=None, strategy=None):

    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)

    format = request.GET.get('format', 'html')
    company_id = request.GET.get('company', utils.get_company(request))
    path = request.GET.get('path', None)
    report = accountifie.reporting.rptutils.get_report(id, company_id, version=version)
    
    if (company_id not in report.works_for):
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render_to_response('404.html', RequestContext(request, {'message': msg})), False

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
        map_values = lambda x: '' if x=='' else str(x['text'])
        for row in report_data:
            writer.writerow([row['label']] + [map_values(row[col]) for col in [x for x in report.column_order if x in row]])
        return response
    elif format == 'html':
        # not bootstrap ... the more custom style for more complex reports
        context = report.html_report_context()
        context['query_string']=request.META['QUERY_STRING']
        context['rows'] = []
        for rec in report_data:
            context['rows'] += report.get_row(rec)

        return render_to_response('report.html', RequestContext(request, context))
    else:
        msg = "Sorry. This format is not recognised : %s" % format
        return render_to_response('404.html', RequestContext(request, {'message': msg})), False


# Run full 5 year monthly projections for 3 main reports

@task
def forecast_run_task(fcast_id, report_id, col_tag, company_ID=utils.get_default_company(), version='v1'):
    fcast = Forecast.objects.get(id=fcast_id)
    strategy = QueryManagerStrategyFactory().get('forecast')
    strategy.set_cache(fcast_id=fcast_id, proj_gl_entries=fcast.get_gl_entries())

    report = accountifie.reporting.rptutils.get_report(report_id, company_ID, version=version)
    report.configure(col_tag=col_tag)
    report.set_gl_strategy(strategy)
    report_data = report.calcs()

    path = os.path.join(settings.DATA_ROOT, 'forecast_%s_%s.csv' %( fcast_id, report_id))
    f = open(path, 'wb')

    writer = csv.writer(f)
    writer.writerow([''] + report.column_order)
    map_values = lambda x: '' if x=='' else str(x['text'])
    for row in report_data:
        writer.writerow([row['label']] + [map_values(row[col]) for col in [x for x in report.column_order if x in row]])
    f.close()
    
    

@login_required
def forecast_run(request):
    fcast_id = request.GET['forecast']
    report_id = request.GET['report']
    col_tag = request.GET['col_tag']
    result, out, err = forecast_run_task(fcast_id, report_id, col_tag, 
                                        task_title='Forecast %s %s' % (fcast_id, report_id),
                                        task_success_url=reverse('fcast_finished'))

    if result != 0:
        #error starting task, warn the user
        context = {'file_name': file_name, 'success': False, 
                        'out': out, 'err': err}
        messages.error(request, 'Could not run the forecast, please\
                       see below')
        if (len(err)):
            messages.warning(request, err)
        if (len(out)):
            messages.info(request, mark_safe('<pre>%s</pre>' % out))
        return forecast_detail(request, fid)
    else:
        return HttpResponseRedirect(reverse('task_result', kwargs={'pid':
                                                                   out}))
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


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
    return render_to_response('forecasts/forecast_detail.html', context, RequestContext(request))



