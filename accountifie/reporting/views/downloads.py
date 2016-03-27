import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import accountifie.reporting.api
import accountifie.gl.apiv1 as gl_api
import accountifie.toolkit.utils as utils


@login_required
def download_ledger(request):
    from_date, to_date = utils.extractDateRange(request)
    company_ID = utils.get_company(request)

    accts = gl_api.accounts()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ledger.csv"'
    writer = csv.writer(response)

    header_row = ['id', 'date', 'comment', 'contra_accts', 'counterparty', 'amount', 'balance']

    for acct in accts:
        history = accountifie.reporting.api.history({'type': 'account', 'from_date': from_date, 'to_date': to_date, 'company_ID': company_ID, 'id': acct['id']})
        if len(history) > 0:
            writer.writerow([])
            writer.writerow([acct['id'], acct['display_name'], acct['path']])
            writer.writerow([])
            writer.writerow(header_row)
            for idx in history.index:
                writer.writerow([history.loc[idx, col] for col in header_row])
    
    return response

