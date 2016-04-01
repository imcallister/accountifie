import datetime

from accountifie.common.api import api_func
import accountifie.query.query_manager as QM


def balances(company_id, qstring={}):
    as_of = qstring.get('as_of', datetime.datetime.now().date())

    # no way right now to know whether which company it is in
    data = QM.QueryManager().pd_acct_balances(company_id, {as_of.isoformat(): as_of})
    return data[as_of.isoformat()].to_dict()