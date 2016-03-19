import json
from dateutil.parser import parse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

import accountifie.reporting.api

import logging
logger = logging.getLogger('default')


def api(request, api_view):
    params = request.GET
    return HttpResponse(json.dumps(accountifie.reporting.api.get(api_view, params), cls=DjangoJSONEncoder), content_type="application/json")

def balance_trends(request):
    dt = parse(request.GET.get('date'))
    acct_list = request.GET.get('acct_list').split('.')

    return HttpResponse(json.dumps(accountifie.reporting.api.balance_trends(dt, acct_list), cls=DjangoJSONEncoder), content_type="application/json")
