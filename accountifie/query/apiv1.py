from decimal import Decimal
from accountifie.query.query_manager import QueryManager
import datetime


def acct_balances(company_id, as_of, filter_closing_entries=False):
    qm = QueryManager()
    if type(as_of) == list:
        dates = as_of
    else:
        dates = [as_of]

    return qm.gl_strategy.account_balances_for_dates(company_id,
                                         None,
                                         dates,
                                         None, None, None,
                                         filter_closing_entries=filter_closing_entries)

def cp_balances(company_id, qstring):
    as_of = qstring.get('date', datetime.datetime.now().date())
    account_id = qstring.get('account')
    qm = QueryManager()
    dates_dict = {'date': as_of}
    return qm.cp_balances(company_id, dates_dict, acct_list=[account_id])[account_id]['date']['closingBalance']

def cp_balance_changes(company_id, qstring):
    dates = qstring.get('date', datetime.datetime.now().date())
    account_id = qstring.get('account')
    qm = QueryManager()
    dates_dict = {'date': dates}

    results = qm.cp_balances(company_id, dates_dict, acct_list=[account_id])[account_id]['date']

    def _get_chg(cp):
        return closing.get(cp, Decimal('0')) - opening.get(cp, Decimal('0'))
    
    closing = dict((l['cp'], Decimal(l['total'])) for l in results['closingBalance'])
    opening = dict((l['cp'], Decimal(l['total'])) for l in results['openingBalance'])
    all_cps = list(set(list(opening.keys()) + list(closing.keys())))
    return [{'total': str(_get_chg(cp)), 'cp': cp} for cp in all_cps]
    