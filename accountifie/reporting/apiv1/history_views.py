import datetime

from django.conf import settings

from accountifie.common.api import api_func
import accountifie.query.query_manager as QM
from accountifie.toolkit.utils import start_of_year

import logging

logger = logging.getLogger('default')


def transaction(trans_id, qstring={}):
    # no way right now to know whether which company it is in
    companies = [cmpy['id'] for cmpy in api_func('gl', 'companies') if cmpy['cmpy_type']=='ALO']
    for cmpny in companies:
        info = QM.QueryManager().transaction_info(cmpny, trans_id)
        if len(info)>0:
            return info
    
    return None


def _account_history(acct_id, company_ID, from_date, to_date, cp):
    return QM.QueryManager().pd_history(company_ID, 'account', acct_id, from_date=from_date, to_date=to_date, cp=cp)


def _cp_history(cp_id, company_ID, from_date, to_date):
    return QM.QueryManager().pd_history(company_ID, 'account', '3000', from_date=from_date, to_date=to_date, cp=cp_id)
        
    
def history(id, qstring={}):

    start_cutoff = qstring.get('from_date', None)
    start_date = settings.DATE_EARLY
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    cp = qstring.get('cp', None)

    if not start_cutoff:
        start_cutoff = start_of_year(end_date.year)

    company_ID = qstring.get('company_id', api_func('environment', 'variable', 'DEFAULT_COMPANY_ID'))
    
    if api_func('gl', 'account', str(id)) is not None:
        hist = _account_history(id, company_ID, start_date, end_date, cp)
        return hist[hist['date'] >= start_cutoff].to_dict(orient='records')
    elif api_func('gl', 'counterparty', id) is not None:
        hist = _cp_history(id, company_ID, start_date, end_date)
        return hist[hist['date'] >= start_cutoff].to_dict(orient='records')
    else:
        return "ID %s not recognized as an account or counterparty" %id
    
"""  


    type = 'account'
    if type == 'account':
        acct = api_func('gl', 'account', id)
        display_name = '%s: %s' %(acct['id'], acct['display_name'])
        history = QM.QueryManager().pd_history(company_ID, 'account', acct['id'], from_date=from_date, to_date=to_date, cp=cp)

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
        history = QM.QueryManager().pd_history(company_ID, type, ref, from_date=from_date, to_date=to_date, excl_contra=excl, incl=incl)
        column_titles = ['id', 'date', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'creditor':
        cp_info = api_func('gl', 'counterparty', id)
        
        display_name = '%s: %s' %(cp_info['id'], cp_info['name'])
        history = QM.QueryManager().pd_history(company_ID, 'account', '3000', from_date=from_date, to_date=to_date, cp=id)
        history = history[history['counterparty']==id]
        history['balance'] = history['amount'].cumsum()

        column_titles = ['id', 'date', 'comment', 'contra_accts', 'amount', 'balance']
    else:
        raise ValueError('This type of history is not supported')

    return history.to_dict(orient='records')


def balance_trends(params):
    dt = parse(params['date'])

    accounts = api_func('gl', 'accounts')
    if 'accts_path' in params:
        acct_list = [x['id'] for x in accounts if params['accts_path'] in x['path']]
    else:
        acct_list = params['acct_list'].split('.')
    
    gl_strategy = params.get('gl_strategy', None)
    company_id = params.get('company_id', utils.get_default_company())
    
    # 3 months for now
    report = get_report('AccountActivity', company_id, version='v1')
    report.set_gl_strategy(gl_strategy)

    M_1 = utils.end_of_prev_month(dt.month, dt.year)
    M_2 = utils.end_of_prev_month(M_1.month, M_1.year)

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
    company_ID = request.GET.get('company', utils.get_company(request))
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
"""