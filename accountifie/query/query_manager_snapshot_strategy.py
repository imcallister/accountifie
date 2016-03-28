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

import dateutil.parser
import pandas as pd
import datetime

from django.conf import settings
import django.core.cache

import accountifie.toolkit.utils as utils
from functools import partial
from query_manager_strategy import QueryManagerStrategy
from accountifie.common.api import api_func

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
    

class QueryManagerSnapshotStrategy(QueryManagerStrategy):


    def set_cache(self, snapshot_time, extra=None):
        self.snapshot_time = snapshot_time
        try:
            self.url = api_func('environment', 'variable', 'ACCOUNTIFIE_SVC_URL')
        except:
            self.url = settings.ACCOUNTIFIE_SVC_URL
        if extra:
            self.extra = parse_cache(extra)
        else:
            self.extra = None
            
    def get_all_transactions(self, company_id):

        if self.snapshot_time:
            qs = '?snapshotDate=%s' % self.snapshot_time.strftime('%Y-%m-%dT%H:%M')
        else:
            qs = ''

        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            trans = []
            for cmpny in company_list:
                cmpny_url = ('%s/gl/%s/snapshot-transactions' % (self.url, cmpny)) + qs
                trans += json.load(urllib2.urlopen(cmpny_url))
        else:
            cmpny_url = '%s/gl/%s/snapshot-transactions' % (self.url, company_id)
            cmpny_url += qs
            trans = json.load(urllib2.urlopen(cmpny_url))
        
        return trans



    def get_snap_cache(self, company_id):
        
        if self.snapshot_time:
            qs = '?date=%s' % self.snapshot_time.strftime('%Y-%m-%dT%H:%M')
            # try the in-memory cache first
            memory_cache = django.core.cache.get_cache('default')
            snap_cache = memory_cache.get('snap_%s_%s' % (self.snapshot_time.strftime('%Y-%m-%dT%H:%M'), company_id))
        else:
            qs = ''
            snap_cache = None

        if snap_cache is None:
            # if not then load everything
            
            if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
                company_list = api_func('gl', 'company_list', company_id)
                caches = []
                for cmpny in company_list:
                    cmpny_url = ('%s/gl/%s/snapshot-transactions' % (self.url, cmpny)) + qs
                    caches.append(parse_cache(json.load(urllib2.urlopen(cmpny_url)), company_id=cmpny))
                snap_cache = pd.concat(caches)
            else:
                url = '%s/gl/%s/snapshot-transactions' % (self.url, company_id)
                url += qs
                snap_cache = parse_cache(json.load(urllib2.urlopen(url)), company_id=company_id)
            
            if self.snapshot_time:
                # only save if fixed time
                memory_cache.set('snap_%s_%s' % (self.snapshot_time.strftime('%Y-%m-%dT%H:%M'), company_id), snap_cache, 3600)
                logger.info('saving snap cache to local memory cache')

        if self.extra:
            # add extra to snap_cache
            snap_cache = pd.concat([snap_cache, self.extra])
        return snap_cache



    def get_gl_entries(self, company_id, account_ids, from_date=INCEPTION, to_date=FOREVER):
        cache = self.get_snap_cache(company_id)

        if cache is None:
            return None

        entries = cache[cache['account_id'].isin(account_ids)]
        return entries


    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra):
        date_indexed_account_balances = {}
        entries = self.__pd_balances_prep(company_id, account_ids, excl_interco=excl_interco, excl_contra=excl_contra, with_counterparties=with_counterparties)

        if entries is None:
            return {dt: { account: float(0) for account in account_ids } for dt in dates}

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']

            sub_entries = self.__depreciation_calcs(start, end, entries)
            col = sub_entries[['account_id', 'amount']].groupby('account_id').sum()['amount']
            date_indexed_account_balances[dt] = col.to_dict()

        return date_indexed_account_balances

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        
        all_entries = self.get_gl_entries(company_id, account_ids)

        period_entries = []
        from_date = dateutil.parser.parse(from_date).date() if isinstance(from_date, basestring) else from_date
        to_date =   dateutil.parser.parse(to_date).date()   if isinstance(to_date, basestring) else to_date
        all_entries = all_entries[all_entries['date']>=from_date]

        periods = [{'from': from_date, 'to': to_date}]
        if chunk_frequency == 'end-of-month':
            periods = self.monthly_chunk_periods(from_date, to_date)
        else:
            raise Exception('Unknown chunk frequency: %s' % chunk_frequency)


        clean_end = lambda row: row['date_end'] if row['date_end'] else row['date']
        clean_id = lambda row: str(row['id'])
        
        for period in periods:
            start = period['from']
            end = period['to']

            entries = all_entries[(all_entries.date <= end) & (all_entries.date_end >= start)]
            #entries = self.get_gl_entries(company_id, account_ids, from_date=start, to_date=end)

            if entries is not None and not entries.empty:
                if excl_contra and not entries.empty:
                    for contra in excl_contra:
                        entries = entries[entries.contra_accts.map(lambda x: contra not in x.split(','))]

                if with_counterparties:
                  entries = entries[entries['counterparty'] in with_counterparties]

                if excl_interco and not entries.empty:
                    entries = entries[~entries.apply(self.__inter_co, axis=1)]

                if entries.empty:
                    break

                entries['transaction_id'] = entries.apply(clean_id, axis=1)
                entries['date_end'] = entries.apply(clean_end, axis=1)
                sub_entries = self.__depreciation_calcs(start, end, entries)

                sub_entries.reset_index(drop=False, inplace=True)
                sub_entries.rename(columns={'transaction_id': 'id'}, inplace=True)
                period_entries.append(sub_entries)

        if len(period_entries) == 0:
            return None
        else:
            all_entries = pd.concat(period_entries, ignore_index=True).reset_index()
            all_entries['contra_accts'] = 'missing'
            return all_entries[['date', 'id', 'comment', 'account_id', 'counterparty', 'contra_accts', 'amount']].to_dict()

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
        companies = [cmpy['id'] for cmpy in api_func('gl', 'companies')]
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
