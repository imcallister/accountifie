from decimal import Decimal
import csv

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext, Context
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from accountifie.cal.models import Year
from accountifie.common.api import api_func
import accountifie.reporting.apiv1 as rptg_api
import accountifie.query.query_manager
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils as rptutils

import logging

logger = logging.getLogger('default')



ACCT_DEF = {
    'id': {'link': lambda x: "/api/reporting/transaction/%s" % x},
    'date': {},
    'comment': {},
    'account_id': {'link': lambda x: "/reporting/history/account/%s" % x},
    'contra_accts': {'link': lambda x: "/reporting/history/account/%s" % x},
    'counterparty': {'link': lambda x: "/reporting/history/creditor/%s" % x},
    'amount': {'fmt': lambda x: "{:,.2f}".format(Decimal(x))},
    'balance': {'fmt': lambda x: "{:,.2f}".format(Decimal(x))}
}

def create_entry(value, fmtr, qs):
    entry = {'text': fmtr['fmt'](value) if 'fmt' in fmtr else value}
    if 'link' in fmtr:
        entry['link'] = fmtr['link'](value)
        if qs:
            entry['link'] += '?%s' % qs
    return entry


def create_row(row, col_order, qs=None, fmtr=ACCT_DEF):
    return [create_entry(row[i], fmtr[i], qs=qs) for i in col_order]

@login_required
def history(request, type, id):
    qs = request.GET.urlencode()
    config = rptutils.history_prep(request)
    as_csv = (request.GET.get('as_csv', 'false').lower() == 'true')

    if type == 'account':
        acct = api_func('gl', 'account', id)
        display_name = '%s: %s' %(acct['id'], acct['display_name'])
        column_titles = ['id', 'date', 'comment', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'path':
        id = id.replace('_', '.')
        display_name = 'path: %s' % id
        column_titles = ['id', 'date', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount', 'balance']
    elif type == 'creditor':
        cp_info = api_func('gl', 'counterparty', id)
        display_name = '%s: %s' %(cp_info['id'], cp_info['name'])
        column_titles = ['id', 'date', 'comment', 'contra_accts', 'amount', 'balance']
    else:
        raise ValueError('This type of history is not supported')
    

    hist_rslts = rptg_api.history(id, config)
    if as_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow(column_titles)
        for h in hist_rslts:
            writer.writerow([h[col] for col in column_titles])
        return response

    else:
        if hist_rslts:
            entries = [create_row(h, column_titles, qs=qs) for h in hist_rslts]
        else:
            entries = []
        
        context = {}
        context['display_name'] = display_name
        context['column_titles'] = column_titles
        context['history'] = entries
        context['years'] = Year.objects.all()
        context['by_date_cleared'] = False
        context['from_date'] = config.get('from', settings.DATE_EARLY)
        context['to_date'] = config.get('to', settings.DATE_LATE)
        return render(request, 'history.html', context)
