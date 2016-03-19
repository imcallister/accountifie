from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.reporting.rptutils import get_report_cols

import accountifie.toolkit.utils as utils


@login_required
def bstrap_report(request, rpt_id):
    # need to go thru first stage of report building to set columns
    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)
    company_ID = request.GET.get('company', utils.get_company(request))
    qs = request.META[' _STRING']
    
    cols, col_order = get_report_cols(rpt_id, company_ID, as_of=as_of, col_tag=col_tag)
    context = {'cols': zip(['label'] + col_order, ['nameFormatter'] + ['valueFormatter'] * len(col_order))}

    data_url = '/reporting/api/%s' % rpt_id
    if qs != '':
        data_url += '?%s' % qs
    
    context['data_url'] = data_url

    return render_to_response('bstrap_report.html', context, context_instance = RequestContext(request))
