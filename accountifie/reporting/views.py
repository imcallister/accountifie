import os
import pandas as pd
import csv
import json
import urllib2
from dateutil.parser import parse

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.serializers.json import DjangoJSONEncoder

from accountifie.cal.models import Year

import accountifie.reporting.models
import accountifie.gl.api
import accountifie.reporting.api
import accountifie.query.query_manager

import accountifie._utils

import logging

logger = logging.getLogger('default')

class Something():
    pass


def api(request, api_view):
    params = request.GET
    return HttpResponse(json.dumps(accountifie.reporting.api.get(api_view, params), cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def download_ledger(request):
    from_date, to_date = accountifie._utils.extractDateRange(request)
    company_ID = accountifie._utils.get_company(request)

    accts = accountifie.gl.api.accounts({})
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ledger.csv"'
    writer = csv.writer(response)

    header_row = ['id', 'date', 'comment', 'contra_accts', 'counterparty', 'amount', 'balance']

    for acct in accts:
        history = accountifie.reporting.api.history({'type': 'account', 'from_date': from_date, 'to_date': to_date, 'company_ID': company_ID, 'id': acct['id']})
        if len(history) > 0:
            writer.writerow([])
            writer.writerow([acct['id'], acct['display_name'], acct['path']])
            writer.writerow([])
            writer.writerow(header_row)
            for idx in history.index:
                writer.writerow([history.loc[idx, col] for col in header_row])
    
    return response

def cparty_payment_summary(request):
    from_date, to_date = accountifie._utils.extractDateRange(request)
    company_id = accountifie._utils.get_company(request)
    qm = accountifie.query.query_manager.QueryManager()

    cp_totals = qm.balance_by_cparty(company_id, ['1001'], from_date=from_date, to_date=to_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="1099s.csv"'
    writer = csv.writer(response)

    writer.writerow(['Payments to Counterparties for period from %s to %s' %(from_date.isoformat(), to_date.isoformat())])
    writer.writerow(['Counterparty', 'Amount'])

    for cp in cp_totals.index:
        if cp_totals.loc[cp] <0:
            cp_name = accountifie.gl.api.counterparty({'id': cp})['name']
            writer.writerow([cp_name, -cp_totals.loc[cp]])

    return response



def balance_trends(request):
    dt = parse(request.GET.get('date'))
    acct_list = request.GET.get('acct_list').split('.')

    return HttpResponse(json.dumps(accountifie.reporting.api.balance_trends(dt, acct_list), cls=DjangoJSONEncoder), content_type="application/json")
    

@login_required
def bstrap_report(request, rpt_id):
    # need to go thru first stage of report building to set columns
    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)
    company_ID = request.GET.get('company', accountifie._utils.get_company(request))
    qs = request.META[' _STRING']
    
    cols, col_order = accountifie.reporting.models.get_report_cols(rpt_id, company_ID, as_of=as_of, col_tag=col_tag)
    context = {'cols': zip(['label'] + col_order, ['nameFormatter'] + ['valueFormatter'] * len(col_order))}

    data_url = '/reporting/api/%s' % rpt_id
    if qs != '':
        data_url += '?%s' % qs
    
    context['data_url'] = data_url

    return render_to_response('bstrap_report.html', context, 
          context_instance = RequestContext(request)
          )


def create_report(request):

    if 'date' in request.GET:
        dt = request.GET.get('date')
        rpt = request.GET.get('rpt')
        url = '/reporting/reports/%s?date=%s' % (rpt, dt)
    elif 'mth' in request.GET:
        mth = request.GET.get('mth')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/reporting/reports/%s?col_tag=%sM%s' % (rpt, yr, mth)
    elif 'qtr' in request.GET:
        qtr = request.GET.get('qtr')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/reporting/reports/%s?col_tag=%sQ%s' % (rpt, yr, qtr)    
    else:
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        period = request.GET.get('period')
        url = '/reporting/reports/%s?col_tag=%s%s' % (rpt, yr, period)    

    return HttpResponseRedirect(url)

ACCT_DEF = {
    'id': {'link': lambda x: "/reporting/api/transaction_info?id=%s" % x},
    'date': {},
    'comment': {},
    'account_id': {'link': lambda x: "/reporting/history/account/%s" % x},
    'contra_accts': {'link': lambda x: "/reporting/history/account/%s" % x},
    'counterparty': {'link': lambda x: "/reporting/history/creditor/%s" % x},
    'amount': {'fmt': lambda x: "{:,.2f}".format(x)},
    'balance': {'fmt': lambda x: "{:,.2f}".format(x)}
}

def create_entry(value, fmtr):
    entry = {'text': fmtr['fmt'](value) if 'fmt' in fmtr else value}
    if 'link' in fmtr:
        entry['link'] = fmtr['link'](value)
    return entry


def create_row(row, col_order, fmtr=ACCT_DEF):
    return [create_entry(row[i], fmtr[i]) for i in col_order]

@login_required
def history(request, type, id):
    from_date, to_date = accountifie._utils.extractDateRange(request)
    company_ID = accountifie._utils.get_company(request)

    if type == 'account':
        cp = request.GET.get('cp',None)
        
        acct = accountifie.gl.api.account({'id': id})

        display_name = '%s: %s' %(acct['id'], acct['display_name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, 'account', acct['id'], from_date=from_date, to_date=to_date, cp=cp)

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
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, type, ref, from_date=from_date, to_date=to_date, excl_contra=excl, incl=incl)
        column_titles = ['id', 'date', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'creditor':
        cp = request.GET.get('cp',None)
        cp_info = accountifie.gl.api.counterparty({'id': id})
        
        display_name = '%s: %s' %(cp_info['id'], cp_info['name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, 'account', '3000', from_date=from_date, to_date=to_date, cp=id)
        history = history[history['counterparty']==id]
        history['balance'] = history['amount'].cumsum()

        column_titles = ['id', 'date', 'comment', 'contra_accts', 'amount', 'balance']
    else:
        raise ValueError('This type of history is not supported')

    years = Year.objects.all()
    entries = []
    if history is not None:
        for i in history.index:
            entries.append(create_row(history.loc[i], column_titles))
    
    context = {}
    context['display_name'] = display_name
    context['column_titles'] = column_titles
    context['history'] = entries
    context['years'] = years
    context['by_date_cleared'] = False
    context['from_date'] = from_date
    context['to_date'] = to_date

    return render_to_response('history.html', RequestContext(request, context))

@login_required
def balance_history(request, type, id):
    from_date, to_date = accountifie._utils.extractDateRange(request)
    company_ID = accountifie._utils.get_company(request)

    if type == 'account':
        cp = request.GET.get('cp',None)
        acct = accountifie.gl.api.account({'id': id})
        display_name = '%s: %s' %(acct['id'], acct['display_name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, 'account', acct['id'], from_date=from_date, to_date=to_date, cp=cp)

        if cp and not history.empty:
            history = history[history['counterparty']==cp]
            display_name += ' -- %s' % cp
        
        balance_history = history[['amount','date']].groupby('date').sum().cumsum().reset_index()
        column_titles = ['date', 'amount']
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
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, type, ref, from_date=from_date, to_date=to_date, excl_contra=excl, incl=incl)
        balance_history = history[['amount','date']].groupby('date').sum().cumsum().reset_index()
        column_titles = ['date', 'amount']
    elif type == 'creditor':
        cp = request.GET.get('cp',None)
        cp_info = accountifie.gl.api.counterparty({'id': id})
        
        display_name = '%s: %s' %(cp_info['id'], cp_info['name'])
        history = accountifie.query.query_manager.QueryManager().pd_history(company_ID, 'account', '3000', from_date=from_date, to_date=to_date, cp=id)
        history = history[history['counterparty']==id]
        balance_history = history[['amount','date']].groupby('date').sum().cumsum().reset_index()
        column_titles = ['date', 'amount']
    else:
        raise ValueError('This type of history is not supported')

    years = Year.objects.all()
    entries = []
    if balance_history is not None:
        for i in balance_history.index:
            entries.append(create_row(balance_history.loc[i], column_titles))
    
    context = {}
    context['display_name'] = display_name
    context['column_titles'] = column_titles
    context['history'] = entries
    context['years'] = years
    context['by_date_cleared'] = False
    context['from_date'] = from_date
    context['to_date'] = to_date

    return render_to_response('bal_history.html', RequestContext(request, context))

def report_prep(request, id):
    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)

    format = request.GET.get('format', 'html')
    company_ID = request.GET.get('company', accountifie._utils.get_company(request))
    path = request.GET.get('path', None)
    report = accountifie.reporting.models.get_report(id, company_ID)
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
