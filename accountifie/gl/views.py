import csv
import logging
import datetime
import json
from dateutil.parser import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

from accountifie.cal.models import Year


from .models import Account, Transaction
import accountifie._utils
import accountifie.gl.api

from accountifie.query.query_manager import QueryManager


fmt = lambda x: "{:,.0f}".format(x)
logger = logging.getLogger('default')


@login_required
def index(request):
    d = {}
    return render_to_response('index.html', RequestContext(request, d))


def api(request, api_view):
    params = request.GET
    return HttpResponse(json.dumps(accountifie.gl.api.get(api_view, params), cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def account(request, id):
    return HttpResponse(json.dumps(accountifie.gl.api.account({'id':id}), cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def accounts(request):
    return HttpResponse(json.dumps(accountifie.gl.api.accounts(), cls=DjangoJSONEncoder), content_type="application/json")
    

@login_required
def download_transactions(request):
    company_ID = accountifie._utils.get_company(request)
    trans = QueryManager().transactions(company_ID)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    writer = csv.writer(response)

    header_row = ['id', 'Comment', 'Type', 'Company', 'Date', 'object_id']

    writer.writerow(header_row)
    for ex in trans:
        writer.writerow(ex)

    return response

@login_required
def download_tranlines(request):
    company_ID = accountifie._utils.get_company(request)
    trans = QueryManager().tranlines(company_ID)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tranlines.csv"'
    writer = csv.writer(response)

    header_row = ['TranLine ID', 'Transaction ID', 'Amount', 'Account Name', 'Counterparty Name', 'Counterparty ID']

    writer.writerow(header_row)
    for ex in trans:
        writer.writerow(ex)

    return response


@login_required
def transaction_info(request, id):
    "Show info about each transaction"
    tran = get_object_or_404(Transaction, pk=id)
    tran = Transaction.objects.get(pk=id)

    source = tran.source_object

    #there's a cleaner way but I can't get it working...
    source_admin_url = '/admin/%s/%s/%s/' % (tran.content_type.app_label, tran.content_type.model, source.pk)

    return render_to_response('gl/transaction_info.html',
        RequestContext(request, dict(
            tran=tran,
            source=source,
            source_admin_url = source_admin_url
            )))



@login_required
def accounts_list(request):
    "Show list of each account"
    accounts = Account.objects.order_by('id')
    return render_to_response('gl/accounts_list.html', RequestContext(request, dict(accounts=accounts)))

