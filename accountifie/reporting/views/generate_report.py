import csv
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.core.serializers.json import DjangoJSONEncoder


import accountifie.reporting.rptutils
import accountifie.toolkit.utils as utils

import logging

logger = logging.getLogger('default')


def report_prep(request, id):
    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)

    format = request.GET.get('format', 'html')
    company_ID = request.GET.get('company', utils.get_company(request))
    path = request.GET.get('path', None)
    report = accountifie.reporting.rptutils.get_report(id, company_ID)
    gl_strategy = request.GET.get('gl_strategy', None)

    if report is None:
        msg = "Report %s does not exist" % id
        return render_to_response('rpt_doesnt_exist.html', RequestContext(request, {'message': msg})), False, None

    if company_ID not in report.works_for:
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render_to_response('rpt_doesnt_exist.html', RequestContext(request, {'message': msg})), False

    report.configure(as_of=as_of, col_tag=col_tag, path=path)
    report.set_gl_strategy(gl_strategy)
    return report, True, format


@login_required
def report(request, id):

    report, is_report, format = report_prep(request, id)

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
        map_values = lambda x: '' if x=='' else str(x['text']).replace('(','-').replace(')','')
        
        for row in report_data:
            if row['fmt_tag'] != 'header':
                writer.writerow([row['label']] + [map_values(row[col]) for col in report.column_order])
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
