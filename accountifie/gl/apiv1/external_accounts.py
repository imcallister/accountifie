import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY,MO,TU,WE,TH,FR

from accountifie.gl.models import ExternalAccount, ExternalBalance
import accountifie.toolkit.utils as utils
import accountifie.query.query_manager

def externalaccounts(qstring={}):
    return [x.gl_account.id for x in ExternalAccount.objects.all().select_related('gl_account')]


def external_bals_history(qstring={}):
    dt = parse(qstring.get('date', datetime.datetime.now().isoformat())).date()
    company_id = qstring.get('company_id', utils.get_default_company())
    gl_strategy = qstring.get('gl_strategy', None)
    
    acct = qstring.get('acct',None)
    dts = list(rrule(DAILY, dtstart=dt + datetime.timedelta(days=-7), until=dt, byweekday=(MO,TU,WE,TH,FR)))
    dts = [dt.date() for dt in dts]

    external_balances = dict((x.date.isoformat(), float(x.balance)) for x in ExternalBalance.objects.filter(account__id=acct).filter(date__in=dts))
    int_bals_df = accountifie.query.query_manager.QueryManager(gl_strategy).pd_acct_balances(company_id, dict((dt.isoformat(),dt) for dt in dts), acct_list=[acct])
    if acct in int_bals_df.index:
        internal_balances = int_bals_df.loc[acct].to_dict()
    else:
        internal_balances = {}
    bal_checks = []
    
    for dt in dts:
        external = external_balances.get(dt.isoformat(), 0.0)
        internal = internal_balances.get(dt.isoformat(), 0.0)
        bal_checks.append({'Date': dt, 'Internal': internal, 'External': external, 'Diff': external - internal})
    
    return bal_checks