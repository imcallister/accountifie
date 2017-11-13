import csv
import logging
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext

import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func
from .models import Counterparty, Account

from accountifie.query.query_manager import QueryManager
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory


fmt = lambda x: "{:,.0f}".format(x)
logger = logging.getLogger('default')


@login_required
def index(request):
    d = {}
    return render(request, 'index.html', d)


@login_required
def download_transactions(request):
    company_id = utils.get_company(request)

    #snapshot_time = datetime.datetime.now()
    strategy = QueryManagerStrategyFactory().get('remote')
    #strategy.set_cache(None)

    trans = strategy.get_all_transactions(company_id)

    all_accts_list = api_func('gl', 'account')
    all_accts = dict((r['id'], r) for r in all_accts_list)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    writer = csv.writer(response)

    writer.writerow(['', '', '', '', '', '','debit', 'debit', 'debit', 'debit','credit', 'credit', 'credit', 'credit'])
    writer.writerow(['Id', 'dateEnd', 'date', 'type', 'comment', 'counterpartyId', 'amount', 'accountId',
                    'account name','counterpartyId', 'amount', 'accountId', 'account name'])

    for ex in trans:
        first_line = ex['lines'][0]
        acct_id = first_line['accountId']
        acct = api_func('gl', 'account', acct_id)
        if (acct['role'] in ['asset', 'expense'] and float(first_line['amount']) >0) or \
            (acct['role'] in ['liability', 'income', 'capital'] and float(first_line['amount']) < 0):
            debit = ex['lines'][0]
            credit = ex['lines'][1]
        else:
            debit = ex['lines'][1]
            credit = ex['lines'][0]

        row = [ex[k] for k in ['bmoId', 'dateEnd', 'date', 'type', 'comment']]
        row += [debit[k] for k in ['counterpartyId', 'amount', 'accountId']]
        row.append(all_accts[debit['accountId']]['display_name'])
        row += [credit[k] for k in ['counterpartyId', 'amount', 'accountId']]
        row.append(all_accts[credit['accountId']]['display_name'])

        writer.writerow(row)

    return response

@login_required
def download_tranlines(request):
    company_id = utils.get_company(request)
    trans = QueryManager().tranlines(company_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tranlines.csv"'
    writer = csv.writer(response)

    header_row = ['TranLine ID', 'Transaction ID', 'Amount', 'Account Name', 'Counterparty Name', 'Counterparty ID']

    writer.writerow(header_row)
    for ex in trans:
        writer.writerow(ex)

    return response



@login_required
def accounts_list(request):
    "Show list of each account"
    accounts = api_func('gl', 'account')
    return render(request, 'gl/accounts_list.html', dict(accounts=accounts))


@login_required
def counterparty_list(request):
    "Show list of each account"
    counterparties = api_func('gl', 'counterparty')
    AP_acct = api_func('environment', 'variable', 'GL_ACCOUNTS_PAYABLE')

    return render(request, 'gl/counterparty_list.html', dict(ap_acct=AP_acct, counterparties=counterparties))
