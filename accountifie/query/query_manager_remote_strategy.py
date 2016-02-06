"""
Strategy that delegates transaction querying to accountifie-svc.

The new kid on the block, capable of going from 0 to 100km/h in under 50ms
though with the chance of a few early speed wobbles.

See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""

import pandas as pd
import json
import accountifie.environment.api
import urllib
import urllib2

from dateutil.parser import parse
from django.conf import settings
from query_manager_strategy import QueryManagerStrategy
import accountifie.gl.api


INTERCO_EXEMPT_ACCOUNTS = ['1001', '1002', '1003', '1004']


class QueryManagerRemoteStrategy(QueryManagerStrategy):
    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra):
        if accountifie.gl.api.get_company({'company_id': company_id})['cmpy_type'] == 'CON':
            company_list = accountifie.gl.api.get_company_list({'company_id': company_id})
            balances = [self.account_balances_for_dates(cmpny, account_ids, dates, with_counterparties, True, excl_contra) for cmpny in company_list]
            return self.__merge_account_balances_for_dates_results(balances)

        
        client = accountifieSvcClient(company_id)
        date_indexed_account_balances = {}

        interco_counterparties = self.get_interco_counterparties_for(company_id) if excl_interco else []
        accounts_with_interco_exclusion =    [id for id in account_ids if id not in INTERCO_EXEMPT_ACCOUNTS] if excl_interco else []
        accounts_without_interco_exclusion = [id for id in account_ids if id in INTERCO_EXEMPT_ACCOUNTS]     if excl_interco else account_ids

        for dt in dates:
            start = dates[dt]['start']
            end = dates[dt]['end']

            interco_excluded_balances = client.balances(
                accounts=accounts_with_interco_exclusion,
                from_date=start,
                to_date=end,
                with_counterparties=with_counterparties,
                excluding_counterparties=interco_counterparties,
                excluding_contra_accounts=excl_contra
            ) if len(accounts_with_interco_exclusion) > 0 else []

            interco_included_balances = client.balances(
                accounts=accounts_without_interco_exclusion,
                from_date=start,
                to_date=end,
                with_counterparties=with_counterparties,
                excluding_contra_accounts=excl_contra
            ) if len(accounts_without_interco_exclusion) > 0 else []

            balances = interco_excluded_balances + interco_included_balances

            date_indexed_account_balances[dt] = dict((balance['id'], float(balance['shift'])) for balance in balances)

        return date_indexed_account_balances

    def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
        if accountifie.gl.api.get_company({'company_id': company_id})['cmpy_type'] == 'CON':
            company_list = accountifie.gl.api.get_company_list({'company_id': company_id})
            balances = [self.transactions(cmpny, account_ids, from_date, to_date, chunk_frequency, with_counterparties, True, excl_contra) for cmpny in company_list]
            return self.__merge_transactions_results(balances)

        client = accountifieSvcClient(company_id)

        interco_counterparties = self.get_interco_counterparties_for(company_id) if excl_interco else []
        accounts_with_interco_exclusion =    [id for id in account_ids if id not in INTERCO_EXEMPT_ACCOUNTS] if excl_interco else []
        accounts_without_interco_exclusion = [id for id in account_ids if id in INTERCO_EXEMPT_ACCOUNTS]     if excl_interco else account_ids

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

        formatted_transactions = []
        for account in transactions:
            for transaction in transactions[account]:
                if transaction['amount'] != '0.00':
                    formatted_transactions.append({
                        'date': parse(transaction['dateEnd'] if ('dateEnd' in transaction and transaction['dateEnd']) else transaction['date']).date(),
                        'id': transaction['id'],
                        'comment': transaction['comment'],
                        'account_id': account,
                        'contra_accts': ','.join(transaction['contraAccounts']),
                        'counterparty': transaction['counterparty'],
                        'amount': float(transaction['amount'])
                    })

        return formatted_transactions

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

    def upsert_transaction(self, transaction):
        client = accountifieSvcClient(transaction['company'])
        client.upsert_transaction(transaction)

    def delete_transaction(self, company_id, transaction_id):
        client = accountifieSvcClient(company_id)
        client.delete_transaction(transaction_id)

    def take_snapshot(self, company_id):
        accountifieSvcClient(company_id).take_snapshot()

    def erase(self, company_id):
        accountifieSvcClient(company_id).erase()

    def set_fast_inserts(self, company_id, value):
        if value:
            accountifieSvcClient(company_id).disable_balance_cache()
        else:
            accountifieSvcClient(company_id).enable_balance_cache()


    @staticmethod
    def __inter_co(row):
        ext_accts = accountifie.gl.api.ext_accounts_list({})
        companies = [cmpy['id'] for cmpy in accountifie.gl.api.companies({}) if cmpy['id']!=company]
        if row['account_id'] in ext_accts:
            return False
        if row['counterparty'] in companies:
            return True
        else:
            return False

    @staticmethod
    def get_interco_counterparties_for(company):
        output = [cmpy['id'] for cmpy in accountifie.gl.api.companies({}) if cmpy['id']!=company and cmpy['cmpy_type']=='ALO']
        output += [x.lower() for x in output]
        return output

class accountifieSvcClient(object):
    def __init__(self, company_id='*'):
        self.company_id = company_id
        self.url_base = "%s/gl/%s" % (self.__accountifie_svc_url(), company_id)

    def __post(self, path, params=None):
        params = json.dumps(params) if params is not None else '{}'
        url = '%s%s' % (self.url_base, path)

        request = urllib2.Request(url, data=params, headers={'Content-Type': 'application/json'})
        response = urllib2.urlopen(request)
        json_result = json.load(response)
        return json_result

    def __get(self, path, params=None):
        if params:
            params = urllib.urlencode(params)
            url = '%s%s?%s' % (self.url_base, path, params)
        else:
            url = '%s%s' % (self.url_base, path)

        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        json_result = json.load(response)

        return json_result

    def balances(self, accounts, from_date=None, to_date=None, with_counterparties=None, excluding_counterparties=None, excluding_contra_accounts=None):
        from_date = None if from_date == '2000-01-01' else from_date
        account_balances = self.__get('/balances', {
            'accounts': ','.join(accounts),
            'from': from_date,
            'to': to_date,
            'withCounterparties': ','.join(with_counterparties or []),
            'excludingCounterparties': ','.join(excluding_counterparties or []),
            'excludingContraAccounts': ','.join(excluding_contra_accounts or [])
        })
        return account_balances

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
            'lines': [{
            'accountId': line['account'],
            'amount': line['amount'],
            'counterpartyId': line['counterparty'],
            'tags': line['tags']
            } for line in transaction['lines']]
        })

    def delete_transaction(self, transaction_id):
        self.__post('/transaction/%s/delete' % transaction_id)

    def erase(self):
        self.__post('/erase')

    def enable_balance_cache(self):
        self.__post('/enable-balance-cache')

    def disable_balance_cache(self):
        self.__post('/disable-balance-cache')

    def take_snapshot(self):
        self.__post('/take-snapshot')

    @staticmethod
    def __accountifie_svc_url():
        return accountifie.environment.api.get('variable', {'name':'ACCOUNTIFIE_SVC_URL'})