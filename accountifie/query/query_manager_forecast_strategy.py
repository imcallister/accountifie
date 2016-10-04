"""
Strategy that performs transaction querying from in memory snapshots.

See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""
import itertools
from functools import partial

import dateutil.parser
import pandas as pd
import datetime

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


class QueryManagerForecastStrategy(QueryManagerStrategy):
    def set_cache(self, hist_strategy=None, fcast_id=None, proj_gl_entries=None):
        self.hist_strategy = hist_strategy
        self.forecast = Forecast.objects.get(id=fcast_id)
        self.cached_projections = self.forecast.get_projections()
        self.calc_balances()
        self.shifts = None
        self.balances = None

    def calc_balances(self):
        # limited task is to 
        # 1) create changes per period... columns = 2016M01, 2016M02 etc
        # 2) create cumulative changes as of each month end

        # changes per period come direct from the projections
        entries = pd.DataFrame(self.cached_projections)
        if entries.empty:
            self.balances = None
            return

        drop_cols = ['Counterparty', 'Company', 'Credit', 'Debit']
        credits = entries.copy()
        credits['account'] = credits['Credit']

        credits = credits[[c for c in credits.columns if c not in drop_cols]]
        debits = entries.copy()
        debits['account'] = debits['Debit']
        debits = debits[[c for c in debits.columns if c not in drop_cols]]

        for col in [c for c in credits.columns if c!='account']:
            credits[col] = credits[col] * -1

        self.shifts = pd.concat([credits, debits]).groupby('account').sum().fillna(0)
        balances_columns = dict((utils.end_of_period(col), col) for col in self.shifts.columns)
        sorted_months = sorted(balances_columns.keys())

        balances = {}
        for i in range(len(sorted_months)):
            label = sorted_months[i].isoformat()
            months_to_date = sorted_months[:i+1]
            shifts_cols = [balances_columns[l] for l in months_to_date]
            balances[label] = self.shifts[shifts_cols].sum(axis=1)

        self.balances = pd.DataFrame(balances)

        return None


    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra, with_tags, excl_tags):
        self.calc_balances()
        date_indexed_account_balances = {}

        # cutoff should be last day of month eg 2016-3-31
        # get balances for the cutoff date
        hist_dates = dict((d, dates[d]) for d in dates if dates[d]['end'] <= self.forecast.start_date)
        proj_dates = dict((d, dates[d]) for d in dates if dates[d]['end'] > self.forecast.start_date)

        hist_qm = query_manager.QueryManager(gl_strategy=self.hist_strategy)
        hist_balances = hist_qm.pd_acct_balances(company_id, hist_dates, acct_list=account_ids, excl_contra=excl_contra, excl_interco=excl_interco, with_tags=with_tags, excl_tags=excl_tags)

        proj_start_dates = {'cutoff': {'start': INCEPTION, 'end': self.forecast.start_date }}
        proj_start_balances = hist_qm.pd_acct_balances(company_id, proj_start_dates, acct_list=account_ids, excl_contra=excl_contra, excl_interco=excl_interco, with_tags=with_tags, excl_tags=excl_tags)

        for dt in proj_dates:
            if utils.is_period_id(dt):
                if self.shifts is not None and dt in self.shifts.columns:
                    balances = self.shifts[dt].fillna(0).to_dict()
                else:
                    balances = {}
            else:
                if dt in self.balances.columns:
                    proj = {}
                    proj['cutoff'] = proj_start_balances['cutoff']
                    proj['fwd'] = self.balances[dt]
                    proj_df = pd.DataFrame(proj).fillna(0)
                    balances = proj_df.sum(axis=1).to_dict()
                else:
                    balances = {}
            date_indexed_account_balances[dt] = dict((balance, float(balances.get(balance,0))) for balance in balances if balance in account_ids)

        for dt in hist_dates:
            date_indexed_account_balances[dt] = hist_balances[dt].fillna(0).to_dict()

        return date_indexed_account_balances

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        msg = "Transactions view not implemented for forecast strategies"
        return render(request, '404.html', {'message': msg}), False









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




    def get_gl_entries(self, company_id, account_ids, from_date=INCEPTION, to_date=FOREVER):
        return self.cached_projections


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
