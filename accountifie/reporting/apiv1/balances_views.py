import datetime

from accountifie.common.api import api_func
import accountifie.query.query_manager as QM


def balances(company_id, qstring={}):
    as_of = qstring.get('as_of', datetime.datetime.now().date().isoformat())
    return QM.QueryManager().pd_acct_balances(company_id, {as_of: as_of})[as_of].to_dict()