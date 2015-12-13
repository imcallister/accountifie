import json
from dateutil.parser import parse
import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

import accountifie._utils
from accountifie.reporting.models import get_report
import accountifie.gl.api
import accountifie.query.query_manager as QM


def get(api_view, params):
    return globals()[api_view](params)


def transaction_info(params):
    trans_id = params['id']
    # no way right now to know whether which company it is in
    companies = [cmpy['id'] for cmpy in accountifie.gl.api.companies({}) if cmpy['cmpy_type']=='ALO']
    for cmpny in companies:
        info = QM.QueryManager().transaction_info(cmpny, trans_id)
        if len(info)>0:
            return info
    
    return None


def balance_trends(params):
    dt = parse(params['date'])

    accounts = accountifie.gl.api.accounts({})
    if 'accts_path' in params:
        acct_list = [x['id'] for x in accounts if params['accts_path'] in x['path']]
    else:
        acct_list = params['acct_list'].split('.')
    
    gl_strategy = params.get('gl_strategy', None)
    company_id = params.get('company_id', accountifie._utils.get_default_company())
    
    # 3 months for now
    report = get_report('AccountActivity', company_id, version='v1')
    report.set_gl_strategy(gl_strategy)

    M_1 = accountifie._utils.end_of_prev_month(dt.month, dt.year)
    M_2 = accountifie._utils.end_of_prev_month(M_1.month, M_1.year)

    three_mth = {}
    three_mth['M_0'] = '%dM%s' % (dt.year, '{:02d}'.format(dt.month))
    three_mth['M_1'] = '%dM%s' % (M_1.year, '{:02d}'.format(M_1.month))
    three_mth['M_2'] = '%dM%s' % (M_2.year, '{:02d}'.format(M_2.month))

    three_mth_order = ['M_2','M_1','M_0']

    col_tag = '%dM%s' % (dt.year, '{:02d}'.format(dt.month))
    report.configure(col_tag=col_tag)
    report.columns = three_mth
    report.column_order = three_mth_order
    report.acct_list = acct_list
    
    return [x for x in report.calcs() if x['fmt_tag']!='header']
    


def report_prep(request, id):

    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)
    format = request.GET.get('format', 'html')
    company_ID = request.GET.get('company', accountifie._utils.get_company(request))
    path = request.GET.get('path', None)
    report = get_report(id, company_ID, version='v1')
    gl_strategy = request.GET.get('gl_strategy', None)

    if company_ID not in report.works_for:
        msg = "This ain't it. Report not available for %s" % company_ID
        return msg, False, None

    report.configure(as_of=as_of, col_tag=col_tag, path=path)
    report.set_gl_strategy(gl_strategy)
    return report, True, format


def html_report_snippet(rpt_id, company_id, as_of=None, col_tag=None, path=None, version='v1', gl_strategy=None):
    report = get_report(rpt_id, company_id, version=version)

    if company_id not in report.works_for:
        msg = "This ain't it. Report not available for %s" % company_ID
        return render_to_response('404.html', RequestContext(request, {'message': report}))

    report.configure(as_of=as_of, col_tag=col_tag, path=path)
    report.set_gl_strategy(gl_strategy)

    report_data = [x for x in report.calcs() if x['fmt_tag']!='header']

    context = report.html_report_context()
    context['rows'] = []
    for rec in report_data:
        context['rows'] += report.get_row(rec)

    return context
