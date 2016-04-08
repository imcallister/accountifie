"""
Strategy that performs transaction querying from in memory snapshots.

See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""
import json
import os
import urllib2
import itertools
from collections import Counter
from functools import partial

import dateutil.parser
import pandas as pd
import datetime

from django.conf import settings

import accountifie.toolkit.utils as utils

from query_manager_strategy import QueryManagerStrategy
import query_manager
from accountifie.common.api import api_func
from accountifie.forecasts.models import Forecast

import logging

logger = logging.getLogger('default')


INCEPTION = datetime.date(2012,12,31)
FOREVER = datetime.date(2099,12,31)


def get_trans_data(tr):
    trans_keys = ['comment', 'dateEnd', 'date', 'type', 'id']
    return dict((k, v) for k, v in tr.iteritems() if k in trans_keys)

def get_contra(tr, account_id):
    return ','.join([x['accountId'] for x in tr['lines'] if x['accountId'] != account_id])


def parse_cache(data, company_id='INC'):
    lines = [[dict(l.items() + get_trans_data(tr).items() + [('contra_accts', get_contra(tr, l['accountId']))]) for l in tr['lines']] for tr in data]

    col_rename = {'accountId': 'account_id', 'dateEnd': 'date_end', 'counterpartyId': 'counterparty'}
    cache = pd.DataFrame(list(itertools.chain(*lines)))
    cache.rename(columns=col_rename, inplace=True)
    cache['date'] = cache['date'].map(lambda x: dateutil.parser.parse(x).date())
    if 'date_end' in cache.columns:
        cache['date_end'] = cache['date_end'].map(lambda x: dateutil.parser.parse(x).date())
        cache['date_end'].fillna(cache['date'], inplace=True)
    else:
        cache['date_end'] = cache['date']
    cache['amount'] = cache['amount'].astype(float)
    if 'Company' in cache.columns:
        cache['columns'] = cache['columns'].fillna(company_id)
    else:
        cache['company'] = company_id

    return cache   


"""
# new setup
self.cut_off
self.hist_strategy    dflts to remote
self.forecast


all balances as sum of:
 -- hist_strategy (via query_manager.QueryManager(gl_strategy=hist_strategy))
 -- balances from self.forecast.projections


"""

class QueryManagerForecastStrategy(QueryManagerStrategy):
    
    def set_cache(self, hist_strategy=None, fcast_id=None, proj_gl_entries=None):
        self.hist_strategy = hist_strategy
        self.forecast = Forecast.objects.get(id=fcast_id)
        self.projections = parse_cache(proj_gl_entries)


    def get_gl_entries(self, company_id, account_ids, from_date=INCEPTION, to_date=FOREVER):
        return self.projections

    def proj_account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra):
        """

        """
        date_indexed_account_balances = {}
        entries = self.__pd_balances_prep(company_id, account_ids, excl_interco=excl_interco, excl_contra=excl_contra, with_counterparties=with_counterparties)
        if entries is None:
            return {dt: { account: 0.0 for account in account_ids } for dt in dates}

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']

            sub_entries = self.__depreciation_calcs(start, end, entries)

            col = sub_entries[['account_id', 'amount']].groupby('account_id').sum()['amount']
            date_indexed_account_balances[dt] = col.to_dict()

        return date_indexed_account_balances


    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra):
        date_indexed_account_balances = {}

        # if date['end'] <= self.cut_off then balances from hist_strategy
        #   query_manager.QueryManager(gl_strategy=hist_strategy).account_balances_for_dates
        # if date['start'] > self.cut_off then balances is sum of balances from hist_strategy plus balances from self.forecast.projections
        # if date['start'] <= self.cut_off and date['end'] > self.cut_off then balances is 

        # 1 get a list of historical dates
        hist_dates = dict((dt, dates[dt]) for dt in [dt for dt in dates if dates[dt]['end'] <= self.forecast.start_date])

        # 2 get a list of spanninh dates
        straddling = [dt for dt in dates if dates[dt]['start'] <= self.forecast.start_date and dates[dt]['end'] > self.forecast.start_date]
        hist_straddle_dates = dict((dt, {'start': dates[dt]['start'], 'end': self.forecast.start_date}) for dt in straddling)
        proj_straddle_dates = dict((dt, {'start': self.forecast.start_date, 'end': dates[dt]['end']}) for dt in straddling)

        # 3 get a list of future dates
        proj_dates = dict((dt, dates[dt]) for dt in [dt for dt in dates if dates[dt]['start'] > self.forecast.start_date])

        hist_qm = query_manager.QueryManager(gl_strategy=self.hist_strategy)
        

        hist_balances = hist_qm.pd_acct_balances(company_id, hist_dates, acct_list=account_ids, excl_contra=excl_contra, excl_interco=excl_interco)
        
        hist_straddle_balances = hist_qm.pd_acct_balances(company_id, hist_straddle_dates, acct_list=account_ids, excl_contra=excl_contra, excl_interco=excl_interco)
        proj_straddle_balances = pd.DataFrame(self.proj_account_balances_for_dates(company_id, account_ids, proj_straddle_dates, with_counterparties, excl_interco, excl_contra))
        
        proj_balances = pd.DataFrame(self.proj_account_balances_for_dates(company_id, account_ids, proj_dates, with_counterparties, excl_interco, excl_contra))
        
        hist_balances[hist_balances.columns] = hist_balances[hist_balances.columns].astype(float)
        hist_straddle_balances[hist_straddle_balances.columns] = hist_straddle_balances[hist_straddle_balances.columns].astype(float)
        proj_straddle_balances[proj_straddle_balances.columns] = proj_straddle_balances[proj_straddle_balances.columns].astype(float)
        proj_balances[proj_balances.columns] = proj_balances[proj_balances.columns].astype(float)
        
        balances = hist_balances.copy()
        
        balances = balances.add(hist_straddle_balances, fill_value=0)
        balances = balances.add(proj_straddle_balances, fill_value=0)
        balances = balances.add(proj_balances, fill_value=0)

        return balances.fillna(0)

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        msg = "Transactions view not implemented for forecast strategies"
        return render_to_response('404.html', RequestContext(request, {'message': msg})), False


    def __pd_balances_prep(self, company_id, account_ids, excl_contra=None, excl_interco=False, with_counterparties=None):
        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            excl_interco = True

        entries = self.get_gl_entries(company_id, account_ids)
        
        if entries is None or entries.empty:
            return None

        if excl_contra:
            for contra in excl_contra:
                entries = entries[entries.contra_accts.map(lambda x: contra not in x.split(','))]

        if excl_interco:
            entries = entries[~entries.apply(self.__inter_co, axis=1)]

        if with_counterparties:
          entries = entries[entries['counterparty'] in with_counterparties]

        if entries.empty:
            return None
        clean_end = lambda row: row['date_end'] if row['date_end'] else row['date']

        entries['date_end'] = entries.apply(clean_end, axis=1)


        return entries

    def __depreciation_calcs(self, start, end, entries):
        extend_comment = lambda row: row['comment'] + (' (prorated)' if row['deprec_factor'] < 1.0 else '')
        sub_entries = entries[(entries.date <= end) & (entries.date_end >= start)]
        _deprec_factor = partial(self.deprec_factor, start=start, end=end)

        if not sub_entries.empty:
            sub_entries.loc[:, 'deprec_factor'] = sub_entries.apply(_deprec_factor, axis=1)
            sub_entries.loc[:, 'comment'] = sub_entries.apply(extend_comment, axis=1)
            sub_entries.loc[:, 'amount'] *= sub_entries['deprec_factor']
            sub_entries.loc[:, 'amount'] = sub_entries['amount'].astype(float)
            #sub_entries.loc[:, 'date'] = sub_entries.apply(lambda row: min(row['date_end'], end), axis=1)
            sub_entries.loc[:, 'date_end'] = sub_entries.apply(lambda row: min(row['date_end'], end), axis=1)
        return sub_entries

    @staticmethod
    def monthly_chunk_periods(from_date, to_date):
        # dates should be from_date, to_date and the first and last days of every month included
        months = list(set(utils.monthrange(from_date, to_date)))
        dates = [(max(utils.start_of_month(x[1], x[0]), from_date), min(utils.end_of_month(x[1], x[0]), to_date)) for x in months]
        periods = [{'from': dt[0], 'to': dt[1]} for dt in dates]
        return periods

    @staticmethod
    def __inter_co(row):
        ext_accts = api_func('gl', 'externalaccounts')
        companies = [cmpy['id'] for cmpy in api_func('gl', 'company')]
        if row['account_id'] in ext_accts:
            return False
        if row['counterparty'] in companies:
            return True
        else:
            return False

    @staticmethod
    def deprec_factor(row, start, end):
        if row['date_end'] is None or row['date_end'] == row['date']:
            return 1.0
        days_outside = float(max((row['date_end'] - end).days, 0) + max((start - row['date']).days, 0))
        expense_period = float((row['date_end'] - row['date']).days + 1)
        deprec_factor = 1.0
        if expense_period > 0:
            deprec_factor -= days_outside / expense_period
        return deprec_factor
