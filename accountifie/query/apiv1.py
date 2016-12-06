from accountifie.query.query_manager import QueryManager
import datetime

def cp_balances(company_id, qstring):
    as_of = qstring.get('date', datetime.datetime.now().date())
    account_id = qstring.get('account')
    qm = QueryManager()
    dates_dict = {'date': as_of}
    return qm.cp_balances(company_id, dates_dict, acct_list=[account_id])[account_id]['date']
