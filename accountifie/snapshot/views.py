import datetime
from decimal import Decimal
import pandas as pd
import json
import csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from accountifie.cal.models import Year

from . import models
from accountifie.common.api import api_func
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
from accountifie.query.query_manager import QueryManager
from accountifie.reporting.rptutils import report_prep
import accountifie.toolkit.utils as utils
from accountifie.common.table import get_table

import logging
logger = logging.getLogger('default')

@login_required
def glsnapshots(request):
    
    context = {}
    context['title'] = 'Snapshots'
    context['content'] = get_table('snapshots')()
    return render(request, 'snapshot/base_snapshot.html', context)



def glsnapshots_balances(request, snap_id):
    snapshot = models.GLSnapshot.objects.get(id=snap_id)
    snapshot_time = snapshot.snapped_at.strftime('%Y-%m-%dT%H:%M:%S.0000ZZ')

    strategy = QueryManagerStrategyFactory().get('snapshot')
    strategy.set_cache(snapshot_time)

    report, is_report, format = report_prep(request, 'RecBalances')
    if not is_report:
        return report

    report.date = snapshot.closing_date
    report.qm_strategy = strategy
    report.snapshot = snapshot
    report.columns = {'snapshot': 'snapshot', 'current': 'current', 'diff': 'diff'}

    report_data = report.calcs()
    
    if format == 'json':
        return HttpResponse(json.dumps(report_data, cls=DjangoJSONEncoder), content_type="application/json")
    elif format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x=='' else str(x['text']).replace('-','0')
        for row in report_data:
            writer.writerow([row['label']] + [map_values(row[col]) for col in report.column_order])
        return response
    elif format == 'html':
        # not bootstrap ... the more custom style for more complex reports
        context = report.html_report_context()
        context['query_string']=request.META['QUERY_STRING']
        context['rows'] = []
        for rec in report_data:
            context['rows'] += report.get_row(rec)

        return render(request, 'report.html', context)
    else:
        msg = "Sorry. This format is not recognised : %s" % format
        return render(request, '404.html', {'message': msg}), False
