"""
Strategy that performs transaction querying locally.
The tried and tested way of doing things, though not as performant as
query_manager_remote_strategy.py.
See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""

import dateutil.parser
import pandas as pd
import accountifie.gl.cache
from accountifie.common.api import api_func

import accountifie.toolkit.utils as utils

from decimal import Decimal, ROUND_HALF_UP
from functools import partial
from .query_manager_strategy import QueryManagerStrategy


class QueryManagerLocalStrategy(QueryManagerStrategy):

    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra):
        date_indexed_account_balances = {}
        entries = self.__pd_balances_prep(company_id,
                                          account_ids,
                                          excl_interco=excl_interco,
                                          excl_contra=excl_contra,
                                          with_counterparties=with_counterparties)

        if entries is None:
            return {dt: {account: Decimal(0) for account in account_ids} for dt in dates}

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']

            sub_entries = self.__depreciation_calcs(start, end, entries)
            col = sub_entries[['account_id', 'amount']].groupby('account_id').sum()['amount']
            date_indexed_account_balances[dt] = col.to_dict()

        return date_indexed_account_balances

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        period_entries = []
        from_date = dateutil.parser.parse(from_date).date() if isinstance(from_date, str) else from_date
        to_date = dateutil.parser.parse(to_date).date() if isinstance(to_date, str) else to_date

        periods = [{'from': from_date, 'to': to_date}]
        if chunk_frequency == 'end-of-month':
            periods = self.monthly_chunk_periods(from_date, to_date)
        else:
            raise Exception('Unknown chunk frequency: %s' % chunk_frequency)

        cache = accountifie.gl.cache.get_cache(company_id)
        clean_end = lambda row: row['date_end'] if row['date_end'] else row['date']
        clean_id = lambda row: str(row['transaction_id'])
        for period in periods:
            start = period['from']
            end = period['to']

            entries = cache.get_gl_entries(account_ids, from_date=start, to_date=end)

            if entries is not None and not entries.empty:
                if with_counterparties:
                    entries = entries[entries['counterparty'] in with_counterparties]

                if excl_contra and not entries.empty:
                    for contra in excl_contra:
                        entries = entries[entries.contra_accts.map(lambda x: contra not in x.split(','))]

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
            all_entries = pd.concat(period_entries, ignore_index=True)
            return all_entries.filter(items=['date', 'id', 'comment', 'account_id', 'contra_accts', 'counterparty', 'amount']).to_dict()

    def __pd_balances_prep(self, company_id, account_ids, excl_contra=None, excl_interco=False, with_counterparties=None):
        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            excl_interco = True

        cache = accountifie.gl.cache.get_cache(company_id)

        entries = cache.get_gl_entries(account_ids)

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


    """
    def create_gl_transactions(self, d2, lines, trans_id, bmo_id):

        
        tran = accountifie.gl.models.Transaction(**d2)
        tran.source_object = d2.pop('source_object')
        tran.bmo_id = bmo_id
        tran.save()

        for l in lines:
            if type(l['account']) in (str,):
                l['account'] = accountifie.gl.models.Account.objects.get(id=l['account'])
            if type(l['counterparty']) in (str,):
                l['counterparty'] = accountifie.gl.models.Counterparty.objects.get(id=l['counterparty'])
            tran.tranline_set.create(account=l['account'],
                                     amount=l['amount'],
                                     counterparty=l['counterparty'],
                                     tags=l['tags'])
    """

    def delete_bmo_transactions(self, company_id, bmo_id):
        logger.info('Deleting transactions: bmo ID=%s, Company=%s' % (company_id, bmo_id))
        for t in accountifie.gl.models.Transaction.objects.filter(bmo_id=bmo_id):
            t.delete()

    def __depreciation_calcs(self, start, end, entries):
        extend_comment = lambda row: row['comment'] + (' (prorated)' if row['deprec_factor'] < Decimal('1') else '')
        sub_entries = entries[(entries.date <= end) & (entries.date_end >= start)]
        _deprec_factor = partial(self.deprec_factor, start=start, end=end)

        if not sub_entries.empty:
            sub_entries.loc[:, 'deprec_factor'] = sub_entries.apply(_deprec_factor, axis=1)
            sub_entries.loc[:, 'comment'] = sub_entries.apply(extend_comment, axis=1)
            sub_entries.loc[:, 'amount'] *= sub_entries['deprec_factor']
            sub_entries.loc[:, 'amount'] = sub_entries['amount'].map(lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
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
            return Decimal('1')
        days_outside = Decimal(max((row['date_end'] - end).days, 0) + max((start - row['date']).days, 0))
        expense_period = Decimal((row['date_end'] - row['date']).days + 1)
        deprec_factor = Decimal('1')
        if expense_period > 0:
            deprec_factor -= days_outside / expense_period
        return deprec_factor