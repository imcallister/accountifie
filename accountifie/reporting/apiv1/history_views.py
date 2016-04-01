import datetime
import pandas as pd

from django.conf import settings

from accountifie.common.api import api_func
import accountifie.query.query_manager as QM
from accountifie.toolkit.utils import start_of_year

import logging

logger = logging.getLogger('default')


def transaction(trans_id, qstring={}):
    # no way right now to know whether which company it is in
    companies = [cmpy['id'] for cmpy in api_func('gl', 'companies') if cmpy['cmpy_type']=='ALO']
    for cmpny in companies:
        info = QM.QueryManager().transaction_info(cmpny, trans_id)
        if len(info)>0:
            return info
    
    return None


def _is_path(path):
    return (path.split('.')[0] in ['assets', 'liabilities', 'equity'])

def _account_history(acct_id, company_ID, from_date, to_date, cp):
    return QM.QueryManager().pd_history(company_ID, 'account', acct_id, from_date=from_date, to_date=to_date, cp=cp)


def _cp_history(cp_id, company_ID , from_date, to_date):
    return QM.QueryManager().pd_history(company_ID, 'account', '3000', from_date=from_date, to_date=to_date, cp=cp_id)
        
    
def _path_history(path, company_ID , from_date, to_date, excl, incl):
    return QM.QueryManager().pd_history(company_ID, 'path', path, from_date=from_date, to_date=to_date, excl_contra=excl, incl=incl)

def _cutoff(start_cutoff, hist):
    used_history = hist[hist['date'] >= start_cutoff]
    unused_history = hist[hist['date'] < start_cutoff][-1:]
    
    unused_history['date'] = start_cutoff
    unused_history['id'] = 'Start'
    for col in [x for x in list(unused_history.columns) if x not in ['id','date','balance']]:
        unused_history[col] = '-'
    
    return pd.concat([unused_history, used_history])
    
def history(id, qstring={}):

    start_cutoff = qstring.get('from_date', None)
    start_date = settings.DATE_EARLY
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    cp = qstring.get('cp', None)
    excl = qstring.get('excl', None)
    incl = qstring.get('incl', None)

    if not start_cutoff:
        start_cutoff = start_of_year(end_date.year)

    company_ID = qstring.get('company_id', api_func('environment', 'variable', 'DEFAULT_COMPANY_ID'))
    
    if api_func('gl', 'account', str(id)) is not None:
        hist = _account_history(id, company_ID, start_date, end_date, cp)
        return _cutoff(start_cutoff, hist).to_dict(orient='records')
    elif api_func('gl', 'counterparty', id) is not None:
        hist = _cp_history(id, company_ID, start_date, end_date)
        return __cutoff(start_cutoff, hist).to_dict(orient='records')
    elif _is_path(id):
        hist = _path_history(id, company_ID, start_date, end_date, excl, incl)
        return _cutoff(start_cutoff, hist).to_dict(orient='records')
    else:
        return "ID %s not recognized as an account or counterparty" %id
