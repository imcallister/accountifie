from decimal import Decimal
import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY,MO,TU,WE,TH,FR

from django.forms.models import model_to_dict

from accountifie.gl.models import Account, ExternalBalance, Counterparty, Company, ExternalAccount
import accountifie.query.query_manager
import accountifie._utils


def get(api_view, params):
    return globals()[api_view](params)


def accounts(params):
    data = list(Account.objects.order_by('id').values())
    return data

def ext_accounts_list(params):
    return [x.gl_account.id for x in ExternalAccount.objects.all()]

def filter_it(x, ex_list):
    for e in ex_list:
        if e in x:
            return False
    return True
    

def path_accounts(params):
    path = params['path']
    excl = params.get('excl', None)
    incl = params.get('incl', None)

    if excl:
        acct_list = [a for a in list(Account.objects.filter(path__contains=str(path)).values()) if filter_it(a['path'], excl)]
    elif incl:
        acct_list = [a for a in list(Account.objects.filter(path__contains=str(path)).values()) if not filter_it(a['path'], incl)]
    else:
        acct_list = [x for x in list(Account.objects.filter(path__contains=str(path)).values())]

    return acct_list


def account(params):
    acct_id = params.get('id', None)
    acct_path = params.get('path', None)
    if acct_id:
        acct = Account.objects.filter(pk=acct_id).first()
    elif acct_path:
        acct = Account.objects.filter(path=acct_path).first()
    else:
        acct = None

    if acct is None:
        return {}
    else:
        return dict((k,v) for k,v in acct.__dict__.iteritems() if k in ['display_name', 'role', 'path', 'id'])

def get_child_paths(path):
    path_len = len(path.split('.'))
    all_sub_paths = [x.path for x in Account.objects.filter(path__contains=path) if len(x.path.split('.')) > path_len]
    all_child_paths = ['.'.join(x.split('.')[:(path_len+1)]) for x in all_sub_paths]
    return list(set(all_child_paths))



def external_bals_history(params):
    dt = parse(params['date']).date()
    company_id = params.get('company_id', accountifie._utils.get_default_company())
    gl_strategy = params.get('gl_strategy', None)
    
    acct = params['acct']
    dts = list(rrule(DAILY, dtstart=dt + datetime.timedelta(days=-7), until=dt, byweekday=(MO,TU,WE,TH,FR)))
    dts = [dt.date() for dt in dts]

    external_balances = dict((x.date.isoformat(), float(x.balance)) for x in ExternalBalance.objects.filter(account__id=acct).filter(date__in=dts))
    internal_balances = accountifie.query.query_manager.QueryManager(gl_strategy).pd_acct_balances(company_id, dict((dt.isoformat(),dt) for dt in dts), acct_list=[acct]).loc[acct].to_dict()

    cols = {dt.isoformat(): dt}
    bal_checks = []
    
    for dt in dts:
        external = external_balances.get(dt.isoformat(), 0.0)
        internal = internal_balances.get(dt.isoformat(), 0.0)
        
        bal_checks.append({'Date': dt, 'Internal': internal, 'External': external, 'Diff': external - internal})
    
    return bal_checks

def get_company(params):
    return model_to_dict(Company.objects.get(id=params['company_id']))

def get_company_color(params):
    return Company.objects.get(id=params['company_id']).color_code

def get_company_list(params):
    company = Company.objects.get(id=params['company_id'])

    if company.cmpy_type == 'ALO':
        return [company.id]
    else:
        return [sub.id for sub in company.subs.all()]
    

def counterparties(params):
    data = list(Counterparty.objects.order_by('id').values())
    return data

def companies(params):
    objs = Company.objects.order_by('id')
    data = []
    for obj in objs:
        entry = dict((fld, getattr(obj, fld)) for fld in ['id','name','cmpy_type'])
        if obj.cmpy_type == 'CON':
            entry['subs'] = [x.id for x in obj.subs.all()]
        data.append(entry)
    return data

def counterparty(params):
    cp_id = params['id']
    cp = Counterparty.objects.filter(id=cp_id).first()
    if cp is None:
        return {}
    else:
        return dict((k,v) for k,v in cp.__dict__.iteritems() if k in ['id','name'])
