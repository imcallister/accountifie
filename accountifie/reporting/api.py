import json
from dateutil.parser import parse
import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext

import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils as rptutils
from accountifie.common.api import api_func
import accountifie.query.query_manager as QM


def get(api_view, params):
    return globals()[api_view](params)


def html_report_snippet(rpt_id, company_id, as_of=None, col_tag=None, path=None, version='v1', gl_strategy=None):
    config = {}
    if as_of:
        config['as_of'] = as_of
    if col_tag:
        config['col_tag'] = col_tag

    report = rptutils.get_report(rpt_id, company_id, version=version)

    report.configure(config)
    report.set_gl_strategy(gl_strategy)

    report_data = [x for x in report.calcs() if x['fmt_tag']!='header']

    context = report.html_report_context()
    context['rows'] = []
    for rec in report_data:
        context['rows'] += report.get_row(rec)

    return context

def balance_trends(params):
    dt = parse(params['date'])

    accounts = api_func('gl', 'account')
    if 'accts_path' in params:
        acct_list = [x['id'] for x in accounts if params['accts_path'] in x['path']]
    else:
        acct_list = params['acct_list'].split('.')
    
    gl_strategy = params.get('gl_strategy', None)
    company_id = params.get('company_id', utils.get_default_company())
    
    # 3 months for now
    report = rptutils.get_report('AccountActivity', company_id, version='v1')
    report.set_gl_strategy(gl_strategy)

    M_1 = utils.end_of_prev_month(dt.month, dt.year)
    M_2 = utils.end_of_prev_month(M_1.month, M_1.year)

    three_mth = {}
    three_mth['M_0'] = '%dM%s' % (dt.year, '{:02d}'.format(dt.month))
    three_mth['M_1'] = '%dM%s' % (M_1.year, '{:02d}'.format(M_1.month))
    three_mth['M_2'] = '%dM%s' % (M_2.year, '{:02d}'.format(M_2.month))

    three_mth_order = ['M_2','M_1','M_0']

    col_tag = '%dM%s' % (dt.year, '{:02d}'.format(dt.month))
    report.configure({'col_tag': col_tag})
    report.columns = three_mth
    report.column_order = three_mth_order
    report.acct_list = acct_list
    
    return [x for x in report.calcs() if x['fmt_tag']!='header']

