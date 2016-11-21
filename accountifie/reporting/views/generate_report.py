import csv
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext, Context
from django.core.serializers.json import DjangoJSONEncoder


import accountifie.reporting.rptutils as rptutils
import accountifie.toolkit.utils as utils

import logging

logger = logging.getLogger('default')



@login_required
def report(request, id):

    report, is_report = rptutils.report_prep(request, id)
    if not is_report:
            return report
        
    if report.from_file:
        try:
            report_data = json.loads(report.from_file)
        except:
            msg = "Sorry. file source is not recognised : %s" % report.from_file
            return render(request, 'rpt_doesnt_exist.html', {'message': msg})
    else:
        report_data = report.calcs()

    if report.format == 'json':
        return HttpResponse(json.dumps(report_data, cls=DjangoJSONEncoder), content_type="application/json")
    elif report.format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x == '' else str(x['text']).replace('(', '-').replace(')', '')
        
        for row in report_data:
            if row['fmt_tag'] != 'header':
                writer.writerow([row['label']] + [map_values(row[col]) for col in report.column_order])
        return response
    elif report.format == 'html':
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
