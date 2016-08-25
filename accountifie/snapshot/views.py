import datetime
from decimal import Decimal
import pandas as pd
import json
import csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from accountifie.cal.models import Year

import models
from accountifie.common.api import api_func
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
from accountifie.query.query_manager import QueryManager
from accountifie.reporting.views import report_prep
import accountifie.toolkit.utils as utils
from accountifie.common.table import get_table

import logging
logger = logging.getLogger('default')

@login_required
def glsnapshots(request):
    
    context = {}
    context['title'] = 'Snapshots'
    context['content'] = get_table('snapshots')()
    return render_to_response('snapshot/base_snapshot.html', context, context_instance=RequestContext(request))



def glsnapshots_balances(request, snap_id):
    snapshot = models.GLSnapshot.objects.get(id=snap_id)
    snapshot_time = snapshot.snapped_at.isoformat()
    logger.info('in glsnapshots_balances with snapshot_time %s' % snapshot_time)
    strategy = QueryManagerStrategyFactory().get('snapshot')
    strategy.set_cache(snapshot_time)

    report, is_report, format = report_prep(request, 'RecBalances')
    if not is_report:
        return report

    report.date = snapshot.closing_date
    report.qm_strategy = strategy
    report.snapshot = snapshot
    report.columns = {'snapshot': 'snapshot', 'current': 'current', 'diff': 'diff'}

    report_data = report.calcs()
    
    if format == 'json':
        return HttpResponse(json.dumps(report_data, cls=DjangoJSONEncoder), content_type="application/json")
    elif format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x=='' else str(x['text']).replace('-','0')
        for row in report_data:
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


"""
def glsnapshots_reconcile(request, snap_id, account_id):
    snapshot = models.GLSnapshot.objects.get(id=snap_id)
    snapshot_time = snapshot.snapped_at
    strategy = QueryManagerStrategyFactory().get('snapshot')
    strategy.set_cache(snapshot_time)

    report, is_report, format = report_prep(request, 'SnapshotRec', version='v1')
    if not is_report:
        return report

    report.qm_strategy = strategy
    report.snapshot = snapshot
    report.account_id = account_id
    
    report_data = report.calcs()
    
    if format == 'json':
        return HttpResponse(json.dumps(report_data, cls=DjangoJSONEncoder), content_type="application/json")
    elif format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x=='' else str(x['text']).replace('-','0')
        for row in report_data:
            writer.writerow([row['label']] + [map_values(row[col]) for col in report.column_order])
        return response
    elif format == 'html':
        # not bootstrap ... the more custom style for more complex reports
        context = report.html_report_context()
        context['query_string']=request.META['QUERY_STRING']
        context['rows'] = []
        for rec in report_data:
            context['rows'] += report.get_row(rec)

        return render_to_response('reporting/report.html', RequestContext(request, context))
    else:
        msg = "Sorry. This format is not recognised : %s" % format
        return render_to_response('404.html', RequestContext(request, {'message': msg})), False




ACCT_DEF = {
    'id_snap': {'link': lambda x: "/gl/transactions/%s" % x},
    'date_snap': {},
    'comment_snap': {},
    'account_id_snap': {'link': lambda x: "/reporting/history/account/%s" % x},
    'contra_accts_snap': {'link': lambda x: "/reporting/history/account/%s" % x},
    'counterparty_snap': {'link': lambda x: "/reporting/history/creditor/%s" % x},
    'amount_snap': {'fmt': lambda x: "{:,}".format(x)},
    'balance_snap': {'fmt': lambda x: "{:,}".format(x)},

    'id_curr': {'link': lambda x: "/gl/transactions/%s" % x},
    'date_curr': {},
    'comment_curr': {},
    'account_id_curr': {'link': lambda x: "/reporting/history/account/%s" % x},
    'contra_accts_curr': {'link': lambda x: "/reporting/history/account/%s" % x},
    'counterparty_curr': {'link': lambda x: "/reporting/history/creditor/%s" % x},
    'amount_curr': {'fmt': lambda x: "{:,}".format(x)},
    'balance_curr': {'fmt': lambda x: "{:,}".format(x)},

}

def create_entry(value, fmtr):
    entry = {'text': fmtr['fmt'](value) if 'fmt' in fmtr else value}
    if 'link' in fmtr:
        entry['link'] = fmtr['link'](value)
    return entry
    

def create_row(row, col_order, fmtr=ACCT_DEF):
    return [create_entry(row[i], fmtr[i]) for i in col_order]


def uniqify(history):
    # where tags are not unique add version numvers
    tag_counts = history['tag'].value_counts()
    dupe_tags = [x for x in tag_counts.index if tag_counts[x]>1]
    for dupe_tag in dupe_tags:
        dupe_indices = history[history['tag']==dupe_tag].index
        for i in range(len(dupe_indices)):
            history.loc[dupe_indices[i], 'tag'] =  history.loc[dupe_indices[i], 'tag'] + '_%d' % i
    return history

@login_required
def history(request, snap_id, account_id):
    from_date, to_date = utils.extractDateRange(request)

    #from_date = datetime.date(to_date.year, 1, 1)

    company_ID = utils.get_company(request)

    snapshot_time = models.GLSnapshot.objects.get(id=snap_id).snapped_at
    strategy = QueryManagerStrategyFactory().get('snapshot')
    strategy.set_cache(snapshot_time)

    snap_history = QueryManager(gl_strategy=strategy).pd_history(company_ID, 'account', account_id, from_date=from_date, to_date=to_date)
    curr_history = QueryManager().pd_history(company_ID, 'account', account_id, from_date=from_date, to_date=to_date)

    if snap_history.empty:
        snap_history = pd.DataFrame(columns=['id','date','comment','amount','balance'])
    if curr_history.empty:
        curr_history = pd.DataFrame(columns=['id','date','comment','amount','balance'])
    # deal with empty history
    snap_history['tag'] = snap_history['comment'] + snap_history['date'].map(lambda x: x.isoformat())
    snap_history = uniqify(snap_history)
    snap_history.set_index('tag', inplace=True)

    curr_history['tag'] = curr_history['comment'] + curr_history['date'].map(lambda x: x.isoformat())
    curr_history = uniqify(curr_history)
    curr_history.set_index('tag', inplace=True) 

    snap_only_history = snap_history.loc[[x for x in snap_history.index if x not in curr_history.index]]
    curr_only_history = curr_history.loc[[x for x in curr_history.index if x not in snap_history.index]]

    history = snap_only_history.join(curr_only_history, how='outer', lsuffix='_snap', rsuffix='_curr')

    for col in ['id_snap', 'comment_snap', 'id_curr', 'comment_curr']:
        history.loc[:, col].fillna('', inplace=True)

    history['date_snap'] = history['date_snap'].fillna(value=history['date_curr'])
    history.sort_index(by='date_snap', inplace=True)

    history['amount_snap'] = history['amount_snap'].fillna(Decimal('0')).map(Decimal)
    history['amount_curr'] = history['amount_curr'].fillna(Decimal('0')).map(Decimal)
    history['balance_snap'] = history['amount_snap'].cumsum()
    history['balance_curr'] = history['amount_curr'].cumsum()

    acct = api_func('gl', 'account', account_id)
    if acct == {}:
        display_name = 'Unknown Account'
    else:
        display_name = '%s: %s' %(acct['id'], acct['display_name'])
    
    base_column_titles = ['id', 'comment', 'amount', 'balance']
    column_titles = ['date_snap'] + [x + '_snap' for x in base_column_titles] + [x + '_curr' for x in base_column_titles] 

    
    years = Year.objects.all()
    entries = []
    if history is not None:
        for i in history.index:
            entries.append(create_row(history.loc[i], column_titles))
    
    return render_to_response('history.html', RequestContext(request,
        dict(display_name=display_name,
            column_titles=column_titles,
            history=entries,
            years=years,
            by_date_cleared=False,
            from_date=from_date,
            to_date=to_date)))


"""