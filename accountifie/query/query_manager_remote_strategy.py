"""
Strategy that delegates transaction querying to accountifie-svc.

The new kid on the block, capable of going from 0 to 100km/h in under 50ms
though with the chance of a few early speed wobbles.

See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""

import pandas as pd
import itertools
import json

try: #python3
    from urllib.request import urlopen
except: #python2
    from urllib2 import urlopen

from decimal import Decimal
from collections import defaultdict

from dateutil.parser import parse
from django.conf import settings
from .query_manager_strategy import QueryManagerStrategy
from accountifie.common.api import api_func
import logging

import time
DZERO = Decimal('0')
logger = logging.getLogger('default')


class QueryManagerRemoteStrategy(QueryManagerStrategy):
    def cp_balances_for_dates(self, company_id, account_ids, dates):        
        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            balances = [self.cp_balances_for_dates(cmpny, account_ids, dates) for cmpny in company_list]
            return self.__merge_cp_balances_for_dates_results(balances)
        
        client = accountifieSvcClient(company_id)
        result = defaultdict(dict)

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']
            cp_balances = client.cp_balances(accounts=account_ids,
                                             from_date=start,
                                             to_date=end)

            for acct_bals in cp_balances:
                result[acct_bals['id']][dt] = {'openingBalance': acct_bals['openingBalance'],
                                               'closingBalance': acct_bals['closingBalance']}

        return result

    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra, with_tags, excl_tags):
        
        interco_exempt_accounts = api_func('gl', 'externalaccounts')

        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            balances = [self.account_balances_for_dates(cmpny, account_ids, dates, with_counterparties, True, excl_contra, with_tags, excl_tags) for cmpny in company_list]
            return self.__merge_account_balances_for_dates_results(balances)

        
        client = accountifieSvcClient(company_id)
        date_indexed_account_balances = {}

        interco_counterparties = self.get_interco_counterparties_for(company_id) if excl_interco else []
        accounts_with_interco_exclusion =    [id for id in account_ids if id not in interco_exempt_accounts] if excl_interco else []
        accounts_without_interco_exclusion = [id for id in account_ids if id in interco_exempt_accounts]     if excl_interco else account_ids

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']

            interco_excluded_balances = client.balances(
                accounts=accounts_with_interco_exclusion,
                from_date=start,
                to_date=end,
                with_counterparties=with_counterparties,
                excluding_counterparties=interco_counterparties,
                excluding_contra_accounts=excl_contra,
                with_tags=with_tags,
                excluding_tags=excl_tags
            ) if len(accounts_with_interco_exclusion) > 0 else []

            interco_included_balances = client.balances(
                accounts=accounts_without_interco_exclusion,
                from_date=start,
                to_date=end,
                with_counterparties=with_counterparties,
                excluding_contra_accounts=excl_contra,
                with_tags=with_tags,
                excluding_tags=excl_tags
            ) if len(accounts_without_interco_exclusion) > 0 else []

            balances = interco_excluded_balances + interco_included_balances
            date_indexed_account_balances[dt] = dict((balance['id'], float(balance['shift'])) for balance in balances)        
        return date_indexed_account_balances

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        interco_exempt_accounts = api_func('gl', 'externalaccounts')

        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            balances = [self.transactions(cmpny, account_ids, from_date, to_date, chunk_frequency, with_counterparties, True, excl_contra) for cmpny in company_list]
            return self.__merge_transactions_results(balances)

        client = accountifieSvcClient(company_id)

        interco_counterparties = self.get_interco_counterparties_for(company_id) if excl_interco else []
        accounts_with_interco_exclusion =    [id for id in account_ids if id not in interco_exempt_accounts] if excl_interco else []
        accounts_without_interco_exclusion = [id for id in account_ids if id in interco_exempt_accounts]     if excl_interco else account_ids

        interco_excluded_transactions = client.transactions(
            accounts=accounts_with_interco_exclusion,
            from_date=from_date,
            to_date=to_date,
            chunk_frequency=chunk_frequency,
            excluding_counterparties=interco_counterparties,
            with_counterparties=with_counterparties,
            excluding_contra_accounts=excl_contra
        ) if len(accounts_with_interco_exclusion) > 0 else {}

        interco_included_transactions = client.transactions(
            accounts=accounts_without_interco_exclusion,
            from_date=from_date,
            to_date=to_date,
            chunk_frequency=chunk_frequency,
            with_counterparties=with_counterparties,
            excluding_contra_accounts=excl_contra
        ) if len(accounts_without_interco_exclusion) > 0 else {}

        # merge the two dictionaries
        transactions = interco_excluded_transactions.copy()
        transactions.update(interco_included_transactions)

        make_contras = lambda x: 'more than two' if len(x)>2 else '.'.join(x)

        formatted_transactions = []
        for account in transactions:
            for transaction in transactions[account]:
                if transaction['amount'] != '0.00':
                    formatted_transactions.append({
                        'date': parse(transaction['dateEnd'] if ('dateEnd' in transaction and transaction['dateEnd']) else transaction['date']).date(),
                        'id': transaction['id'],
                        'comment': transaction['comment'],
                        'account_id': account,
                        'contra_accts': make_contras(transaction['contraAccounts']),
                        'counterparty': transaction['counterparty'],
                        'amount': float(transaction['amount'])
                    })

        return formatted_transactions

    def __merge_cp_balances_for_dates_results(self, result_list):
        merged_results = {}

        for result in result_list:
            for acct in result:
                merged_results[acct] = merged_results[acct] if acct in merged_results else {}
                for date in result[acct]:
                    if date not in merged_results[acct]:
                        merged_results[acct][date] = {'closingBalance': [], 'openingBalance': []}
                    existing_amount = merged_results[acct][date]
                    for col in ['closingBalance', 'openingBalance']:
                        all_rows = existing_amount[col] + result[acct][date][col]
                        merged_results[acct][date][col] = []
                        for k,v in itertools.groupby(sorted(all_rows, key=lambda x: x['cp']), key=lambda x: x['cp']):
                            merged_results[acct][date][col].append({'cp': k, 'total': str(sum(Decimal(r['total']) for r in v))})
        return merged_results

    def __merge_account_balances_for_dates_results(self, result_list):
        merged_results = {}

        for result in result_list:
            for date in result:
                merged_results[date] = merged_results[date] if date in merged_results else {}
                for account in result[date]:
                    existing_amount = merged_results[date][account] if account in merged_results[date] else float(0)
                    merged_results[date][account] = existing_amount + result[date][account]

        return merged_results

    def __merge_transactions_results(self, result_list):
        return [transaction for result in result_list for transaction in result]

    def get_transaction(self, company_id, transaction_id):
        client = accountifieSvcClient(company_id)
        return client.get_transaction(transaction_id)

    def create_gl_transactions(self, d2, lines, trans_id, bmo_id):
        if sum([Decimal(line['amount']) for line in lines]) == DZERO:
            self.upsert_transaction({
                'id': trans_id,
                'bmo_id': bmo_id,
                'date': str(d2['date']),
                'date_end': str(d2.get('date_end', None) or d2['date']),
                'comment': d2['comment'],
                'company': d2['company'],
                'type': None,
                'lines': [dict(account=line['account'],
                                amount=str(Decimal(line['amount'])),
                                counterparty = line['counterparty'],
                                tags = line['tags'] ) for line in lines]
            })
        else:
            logger.info('Unbalanced entry for bmo ID: %s' % bmo_id)


    def upsert_transaction(self, transaction):
        client = accountifieSvcClient(transaction['company'])
        client.upsert_transaction(transaction)

    def delete_transaction(self, company_id, transaction_id):
        client = accountifieSvcClient(company_id)
        client.delete_transaction(transaction_id)

    def delete_bmo_transactions(self, company_id, bmo_id):
        client = accountifieSvcClient(company_id)
        client.delete_bmo_transactions(bmo_id)

    def take_snapshot(self, company_id, snapshot_time=None):
        accountifieSvcClient(company_id).take_snapshot(snapshot_time)

    def erase(self, company_id):
        accountifieSvcClient(company_id).erase()

    def set_fast_inserts(self, company_id, value):
        if value:
            accountifieSvcClient(company_id).disable_balance_cache()
        else:
            accountifieSvcClient(company_id).enable_balance_cache()


    @staticmethod
    def __inter_co(row):
        ext_accts = api_func('gl', 'externalaccounts')
        companies = [cmpy['id'] for cmpy in api_func('gl', 'company') if cmpy['id']!=company]
        if row['account_id'] in ext_accts:
            return False
        if row['counterparty'] in companies:
            return True
        else:
            return False

    @staticmethod
    def get_interco_counterparties_for(company):
        output = [cmpy['id'] for cmpy in api_func('gl', 'company') if cmpy['id']!=company and cmpy['cmpy_type']=='ALO']
        output += [x.lower() for x in output]
        return output

class accountifieSvcClient(object):
    def __init__(self, company_id='*'):
        self.company_id = company_id
        self.url_base = "%s/gl/%s" % (self.__accountifie_svc_url(), company_id)

    def __post(self, path, params=None):
        params = json.dumps(params) if params is not None else '{}'
        url = '%s%s' % (self.url_base, path)
        request = urllib.request.Request(url, data=params, headers={'Content-Type': 'application/json'})
        try:
            response = urlopen(request)
            json_result = json.load(response)
            return json_result
        except:
            logger.error('Accountifie svc post failed on %s with params %s', url, str(params))
            return None

    def __get(self, path, params=None):
        if params:
            params = urllib.parse.urlencode(params)
            url = '%s%s?%s' % (self.url_base, path, params)
        else:
            url = '%s%s' % (self.url_base, path)

        start_time = time.time()
        request = urllib.request.Request(url)
        response = urlopen(request)
        json_result = json.load(response)

        resp_time = time.time() - start_time
        if resp_time > 2:
            logger.info('Accountifie-svc. Long response time. %.2f seconds. URL=%s' % (resp_time, url))

        return json_result

    def balances(self, accounts, from_date=None, to_date=None, with_counterparties=None, excluding_counterparties=None, excluding_contra_accounts=None, with_tags=None, excluding_tags=None):
        from_date = None if from_date == '2000-01-01' else from_date
        account_balances = self.__get('/balances', {
            'accounts': ','.join(accounts),
            'from': from_date,
            'to': to_date,
            'withCounterparties': ','.join(with_counterparties or []),
            'excludingCounterparties': ','.join(excluding_counterparties or []),
            'excludingContraAccounts': ','.join(excluding_contra_accounts or []),
            'withTags': ','.join(with_tags or []),
            'excludingTags': ','.join(excluding_tags or []),
        })

        return account_balances

    def cp_balances(self, accounts, from_date=None, to_date=None):
        from_date = None if from_date == '2000-01-01' else from_date
        cp_balances = self.__get('/cpBalances', {
            'accounts': ','.join(accounts),
            'from': from_date,
            'to': to_date
        })

        return cp_balances

    def transactions(self, accounts, from_date=None, to_date=None, chunk_frequency=None, with_counterparties=None, excluding_counterparties=None, excluding_contra_accounts=None):
        from_date = None if from_date == '2000-01-01' else from_date
        transaction_history = self.__get('/transactions', {
            'accounts': ','.join(accounts),
            'from': from_date,
            'to': to_date,
            'chunkFrequency': chunk_frequency,
            'withCounterparties': ','.join(with_counterparties or []),
            'excludingCounterparties': ','.join(excluding_counterparties or []),
            'excludingContraAccounts': ','.join(excluding_contra_accounts or [])
        })
        return transaction_history


    def get_transaction(self, transaction_id):
        return self.__get('/transaction/%s' % transaction_id)


    def upsert_transaction(self, transaction):
        self.__post('/transaction/%s/upsert' % transaction['id'], {
            'id': transaction['id'],
            'bmoId': transaction['bmo_id'],
            'date': transaction['date'],
            'dateEnd': transaction['date_end'],
            'comment': transaction['comment'],
            'type': transaction['type'],
            'lines': [{'accountId': line['account'],
                       'amount': line['amount'],
                       'counterpartyId': line['counterparty'],
                       'tags': line['tags']
                       }
                      for line in transaction['lines']
                      ]
        })

    def delete_transaction(self, transaction_id):
        self.__post('/transaction/%s/delete' % transaction_id)

    def delete_bmo_transactions(self, bmo_id):
        self.__post('/bmo-transactions/%s/delete' % bmo_id)

    def erase(self):
        self.__post('/erase')

    def enable_balance_cache(self):
        self.__post('/enable-balance-cache')

    def disable_balance_cache(self):
        self.__post('/disable-balance-cache')

    def take_snapshot(self, snapshot_time):
        logger.info('taking snapshot for %s with snapshot_time=%s' % (self.company_id, snapshot_time))
        if snapshot_time:
            self.__post('/snapshot/create?date=%s' % snapshot_time)
        else:
            self.__post('/snapshot/create')

    @staticmethod
    def __accountifie_svc_url():
        return api_func('environment', 'variable', 'ACCOUNTIFIE_SVC_URL')