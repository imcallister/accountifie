

import accountifie.environment.api
import accountifie.gl.api

def get_default_company():
    try:
        return accountifie.environment.api.variable({'name': 'DEFAULT_COMPANY_ID'})
    except:
        return None

def get_trading_company():
    return accountifie.environment.api.variable({'name': 'TRADING_COMPANY_ID'})
    
def get_alias(name):
    try:
        return accountifie.environment.api.alias({'name':name})['display_as']
    except:
        return name

def get_company(request):
    return request.session.get('company_id', get_default_company())

def get_company_name(company_id):
    company_names = dict((entry['id'], entry['name']) for entry in accountifie.gl.api.companies({}))
    try:
        return company_names[company_id]
    except:
        return 'Unknown Company'

def find_first(path, acct_list):
    return min([int(x) for x in acct_list if path in acct_list[x]])

def order_paths(path_list):
    ACCT_LIST = dict((a['id'], a['path']) for a in accountifie.gl.api.accounts({}))
    d = dict((p, find_first(p, ACCT_LIST)) for p in path_list)
    return [x[0] for x in sorted(d.items(), key=operator.itemgetter(1))]
