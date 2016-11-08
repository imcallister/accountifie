from dateutil.parser import parse

from django.contrib.auth.decorators import login_required

import accountifie.toolkit.utils as utils
from accountifie.query.query_manager import QueryManager


def download_ledger(company_id, qs):
    
    # GET DATE PARAMS from request
    from_dt = qs.get('from')
    if type(from_dt) == list:
    	from_dt = from_dt[0]

    if from_dt:
    	trans = QueryManager().transactions(company_id, from_date=parse(from_dt).date())	
    else:
    	trans = QueryManager().transactions(company_id)

    def _get_bmo_id(rec):
        id_parts = rec['id'].split('.')
        return '%s.%s' % (id_parts[0], id_parts[1])

    for tr in trans:
        tr.update({'bmo_id': _get_bmo_id(tr)})

    return sorted(trans, key=lambda x: x['bmo_id'])
