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


def transaction_info(params):
    trans_id = params['id']
    # no way right now to know whether which company it is in
    companies = [cmpy['id'] for cmpy in api_func('gl', 'companies') if cmpy['cmpy_type']=='ALO']
    for cmpny in companies:
        info = QM.QueryManager().transaction_info(cmpny, trans_id)
        if len(info)>0:
            return info
    
    return None

def history(params):
    from_date = params['from_date']
    to_date = params['to_date']
    company_id = params['company_id']
    cp = params.get('cp', None)
    type = params.get('type', None)
    id = params.get('id', None)

    if type == 'account':
        acct = api_func('gl', 'account', id)
        display_name = '%s: %s' %(acct['id'], acct['display_name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_id, 'account', acct['id'], from_date=from_date, to_date=to_date, cp=cp)

        if cp and not history.empty:
            history = history[history['counterparty']==cp]
            history['balance'] = history['amount'].cumsum()
            display_name += ' -- %s' % cp

        column_titles = ['id', 'date', 'comment', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'path':
        ref = id.replace('_','.')
        display_name = 'path: %s' % ref
        excl = request.GET['excl'].split(',') if request.GET.has_key('excl') else None
        incl = request.GET['incl'].split(',') if request.GET.has_key('incl') else None
        if excl:
            excl = [x.replace('_','.') for x in excl]
            display_name += '  -- excl %s' % ','.join(excl)
        if incl:
            incl = [x.replace('_','.') for x in incl]
            display_name += '  -- incl %s' % ','.join(incl)
        history = accountifie.query.query_manager.QueryManager().pd_history(company_id, type, ref, from_date=from_date, to_date=to_date, excl_contra=excl, incl=incl)
        column_titles = ['id', 'date', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'creditor':
        cp_info = api_func('gl', 'counterparty', id)
        
        display_name = '%s: %s' %(cp_info['id'], cp_info['name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_id, 'account', '3000', from_date=from_date, to_date=to_date, cp=id)
        history = history[history['counterparty']==id]
        history['balance'] = history['amount'].cumsum()

        column_titles = ['id', 'date', 'comment', 'contra_accts', 'amount', 'balance']
    else:
        raise ValueError('This type of history is not supported')

    return history


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
    


def report_prep(request, id):

    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)
    format = request.GET.get('format', 'html')
    company_id = request.GET.get('company', utils.get_company(request))
    path = request.GET.get('path', None)
    report = rptutils.get_report(id, company_id, version='v1')
    gl_strategy = request.GET.get('gl_strategy', None)

    if company_id not in report.works_for:
        msg = "This ain't it. Report not available for %s" % company_id
        return msg, False, None

    report.configure(as_of=as_of, col_tag=col_tag, path=path)
    report.set_gl_strategy(gl_strategy)
    return report, True, format


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
