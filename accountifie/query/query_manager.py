import pandas as pd
import numpy as np
import itertools
from . import query_manager_strategy_factory

from django.conf import settings

import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func

import logging
logger = logging.getLogger('default')


def _get_acct_list(acct_list, paths):
        if acct_list:
            return acct_list
        else:
            if paths:
                accts = list(itertools.chain(*[api_func('gl', 'path_accounts', p) for p in paths]))
                return [x['id'] for x in accts]
            else:
                return [x['id'] for x in api_func('gl', 'path_accounts', '')]


class QueryManager:

    def __init__(self, gl_strategy=None):
        if gl_strategy:
            if isinstance(gl_strategy, str):
                strategy_inst = query_manager_strategy_factory.QueryManagerStrategyFactory().get(strategy=gl_strategy)
            else:
                strategy_inst = gl_strategy
        else:
            strategy_inst = query_manager_strategy_factory.QueryManagerStrategyFactory().get()
        self.gl_strategy = strategy_inst


    def acct_balances(self, company_id, as_of):
        return self.gl_strategy \
                   .account_balances_for_dates(company_id,
                                               None,
                                               [as_of],
                                               None, None, None)[as_of]

    ## REFERENCES: 0 internal, 2 external
    def path_drilldown(self, company_id, dates, path, excl_contra=None, excl_interco=None):
        paths = api_func('gl', 'child_paths', path)
        output = self.pd_path_balances(company_id, dates, paths, excl_contra=excl_contra, excl_interco=excl_interco)
        return output
    
    
    def cp_balances(self, company_id, dates, paths=None, acct_list=None, excl_contra=None, excl_interco=False, with_tags=None, excl_tags=None):

        accts = _get_acct_list(acct_list, paths)
        dates_dict = dict((dt, utils.get_dates_dict(dates[dt])) for dt in dates)
        balances = self.gl_strategy.cp_balances_for_dates(company_id, accts, dates_dict)

        # filter empties
        for acct in balances:
            for dt in balances[acct]:
                for col in ['openingBalance', 'closingBalance']:
                    balances[acct][dt][col] = [l for l in balances[acct][dt][col] if abs(float(l['total'])) > 0.0]
        return balances


    def pd_path_balances(self, company_id, dates, paths, filter_zeros=True, assets=False, excl_contra=None, excl_interco=False, with_tags=None, excl_tags=None):

        path_accts = dict((p, [x['id'] for x in api_func('gl', 'path_accounts', p)]) for p in paths)
        acct_list = list(itertools.chain(*[path_accts[p] for p in paths]))

        dates_dict = dict((dt, utils.get_dates_dict(dates[dt])) for dt in dates)
        date_indexed_account_balances = self.gl_strategy.account_balances_for_dates(company_id, acct_list, dates_dict, None, excl_interco, excl_contra, with_tags, excl_tags)

        data = {}
        for dt in date_indexed_account_balances:
            account_balances = date_indexed_account_balances[dt]

            tuples = []
            for path in paths:
                path_sum = 0
                for account_id in path_accts[path]:
                    if account_id in account_balances:
                        path_sum -= account_balances[account_id]
                tuples.append((path, path_sum))

            data[dt] = dict(tuples)

        output = pd.DataFrame(data)

        if filter_zeros:
            output['empty'] = output.apply(lambda row: np.all(row.values == 0.0), axis=1)
            output = output[output['empty']==False]
            output.drop('empty', axis=1, inplace=True)

        # adjust assets sign
        if assets:
            asset_factor = output.index.map(lambda x: -1.0 if x[:6] == 'assets' else 1.0)
            for col in output.columns:
                output[col] = output[col] * asset_factor
        return output

    def pd_acct_balances(self, company_id, dates, paths=None, acct_list=None, excl_contra=None, excl_interco=False, cp=None, with_tags=None, excl_tags=None):

        if not acct_list:
            if paths:
                accts = list(itertools.chain(*[api_func('gl', 'path_accounts', p) for p in paths]))
                acct_list = [x['id'] for x in accts]
            else:
                acct_list = [x['id'] for x in api_func('gl', 'path_accounts', '')]

        dates_dict = dict((dt, utils.get_dates_dict(dates[dt])) for dt in dates)

        with_counterparties = [cp.id] if cp else None
        date_indexed_account_balances = self.gl_strategy.account_balances_for_dates(company_id, acct_list, dates_dict, with_counterparties, excl_interco, excl_contra, with_tags, excl_tags)

        # filter empties
        for dt in date_indexed_account_balances:
            d = date_indexed_account_balances[dt]
            date_indexed_account_balances[dt] = {k:d[k] for k in d if d[k] != 0.0}

        output = pd.DataFrame(date_indexed_account_balances).fillna(0)

        if paths:
            a = [[x['id'] for x in api_func('gl', 'path_accounts', path)] for path in paths]
            acct_list = list(itertools.chain(*a))
            return output[output.index.isin(acct_list)]
        elif acct_list:
            filtered_output = output[output.index.isin(acct_list)]
            return filtered_output

        return output

    def transaction_info(self, company_id, trans_id):
        return self.gl_strategy.get_transaction(company_id, trans_id)


    def transactions(self, company_id, from_date=settings.DATE_EARLY, to_date=settings.DATE_LATE):
        acct_list = [x['id'] for x in api_func('gl', 'account')]
        all_entries = self.gl_strategy.transactions(company_id, acct_list, from_date, to_date, 'end-of-month', None, None, None)

        return all_entries


    def pd_history(self, company_id, q_type, id, from_date=settings.DATE_EARLY, to_date=settings.DATE_LATE, excl_interco=None, excl_contra=None, incl=None, cp=None):
        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            excl_interco = True

        if q_type == 'account':
            acct_list = [id]
        elif q_type == 'account_list':
            acct_list = incl
        elif q_type=='path':
            acct_list = [x['id'] for x in api_func('gl', 'path_accounts', id, qstring={'excl': excl_contra, 'incl': incl})]
        else:
            raise ValueError('History not implemented for this type')

        with_counterparties = [cp] if cp else None

        all_entries = self.gl_strategy.transactions(company_id, acct_list, from_date, to_date, 'end-of-month', with_counterparties, excl_interco, excl_contra)
        
        if all_entries is None or len(all_entries) == 0:
            return pd.DataFrame()
    
        all_entries_pd = pd.DataFrame(all_entries)
        all_entries_pd.sort(['date', 'id'], ascending=[1, 0], inplace=True)
    
        cols = ['date', 'id', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount']
    
        top_line = pd.Series(dict((col, None) for col in cols))

        top_line['date'] = utils.day_before(all_entries_pd.iloc[0]['date'])
        top_line['amount'] = 0.0
        top_line['comment'] = 'Opening Balance'

        
        all_entries_pd.reset_index(drop=True, inplace=True)
        all_entries_pd.loc['starting'] = top_line
        all_entries_pd.sort_index(by='date', axis=0, inplace=True)
        all_entries_pd['balance'] = all_entries_pd['amount'].cumsum()
    
        return all_entries_pd[cols + ['balance']]

    def balance_by_cparty(self, company_id, acct_ids, from_date=settings.DATE_EARLY, to_date=settings.DATE_LATE):

        all_entries = self.gl_strategy.transactions(company_id, acct_ids, from_date, to_date, 'end-of-month', None, None, None)
        if all_entries is None or len(all_entries) == 0:
            return pd.DataFrame()

        entries_tbl = pd.DataFrame(all_entries).sort_index(by='date')
        cp_tbl = entries_tbl[['counterparty','amount']].groupby('counterparty').sum()

        filter_small = lambda x: x>0.99 or x<-0.99
        cp_tbl = cp_tbl[cp_tbl['amount'].map(filter_small)]

        cp_tbl = cp_tbl.sort_index(by='amount', ascending=False)
        return cp_tbl['amount']
