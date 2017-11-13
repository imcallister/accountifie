"""
Strategy that delegates transaction querying to a snapshot of accountifie-svc.

It is closely modelled on the remote Strategy
See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""

import time
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from decimal import Decimal

from dateutil.parser import parse
from django.conf import settings
from .query_manager_strategy import QueryManagerStrategy
from accountifie.common.api import api_func
import logging

DZERO = Decimal('0')
logger = logging.getLogger('default')


class QueryManagerSnapshotStrategy(QueryManagerStrategy):

    def set_cache(self, snapshot_time):
        self.snapshot_time = snapshot_time


    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra, with_tags, excl_tags):
        interco_exempt_accounts = api_func('gl', 'externalaccounts')

        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            balances = [self.account_balances_for_dates(cmpny, account_ids, dates, with_counterparties, True, excl_contra, with_tags, excl_tags) for cmpny in company_list]
            return self.__merge_account_balances_for_dates_results(balances)

        client = accountifieSvcSnapshotClient(self.snapshot_time, company_id=company_id)
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

    """
    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        interco_exempt_accounts = api_func('gl', 'externalaccounts')

        if api_func('gl', 'company', company_id)['cmpy_type'] == 'CON':
            company_list = api_func('gl', 'company_list', company_id)
            balances = [self.transactions(cmpny, account_ids, from_date, to_date, chunk_frequency, with_counterparties, True, excl_contra) for cmpny in company_list]
            return self.__merge_transactions_results(balances)

        client = accountifieSvcSnapshotClient(company_id)

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
    """

    def __merge_account_balances_for_dates_results(self, result_list):
        merged_results = {}

        for result in result_list:
            for date in result:
                merged_results[date] = merged_results[date] if date in merged_results else {}
                for account in result[date]:
                    existing_amount = merged_results[date][account] if account in merged_results[date] else float(0)
                    merged_results[date][account] = existing_amount + result[date][account]

        return merged_results

    """
    def __merge_transactions_results(self, result_list):
        return [transaction for result in result_list for transaction in result]

    def get_transaction(self, company_id, transaction_id):
        client = accountifieSvcSnapshotClient(company_id)
        return client.get_transaction(transaction_id)
    """
    


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

class accountifieSvcSnapshotClient(object):
    def __init__(self, snapshot_time, company_id='*'):
        self.company_id = company_id
        self.url_base = "%s/gl/%s/snapshot" % (self.__accountifie_svc_url(), company_id)
        self.snapshot_time = snapshot_time

    def __get(self, path, params=None):
        if params:
            params.update({'snapshotDate': self.snapshot_time})
        else:
            params = {'snapshotDate': self.snapshot_time}

        params = urllib.parse.urlencode(params)
        url = '%s%s?%s' % (self.url_base, path, params)

        start_time = time.time()
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        json_result = json.load(response)

        logger.info('Ran snapshots. %d seconds. URL=%s' % (time.time() - start_time, url))

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

    """
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
    """
    
    @staticmethod
    def __accountifie_svc_url():
        return api_func('environment', 'variable', 'ACCOUNTIFIE_SVC_URL')