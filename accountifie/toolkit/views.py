import os
import csv
import json
from ast import literal_eval
from io import StringIO
import datetime
import gzip
import csv
import datetime
from dateutil.parser import parse

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponseRedirect, HttpResponse


from accountifie.gl.models import Company
from . import utils

logger = logging.getLogger('default')


def company_context(request):
    """Context processor referenced in settings.
    This puts the current company ID into any request context, 
    thus allowing templates to refer to it

    This is not a view.
    """

    company_id = utils.get_company(request)
    data = {'company_id': company_id}
    if company_id:
        try:
            company = Company.objects.get(pk=company_id)
            data.update({'company': company})
        except Company.DoesNotExist:
            pass
    return data


@login_required
def choose_company(request, company_id):
    "Hit this to switch companies"

    company_list = [x.id for x in Company.objects.all()]

    if company_id not in company_list:
        raise ValueError('%s is not a valid company' % company_id)
    request.session['company_id'] = company_id
    dest = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(dest)



@user_passes_test(lambda u: u.is_superuser)
def dump_fixtures(request):
    output = StringIO()

    fixture = request.GET.get('fixture', None)

    try:
        if fixture:
            call_command('dumpdata', fixture, '--indent=2', stdout=output)
        else:
            call_command('dumpdata', '--indent=2', stdout=output)

        data = output.getvalue()
        output.close()

        if fixture:
            file_label = 'fixtures_%s_%s' % (fixture, datetime.datetime.now().strftime('%d-%b-%Y_%H-%M'))
        else:
            file_label = 'fixtures_all_%s' % datetime.datetime.now().strftime('%d-%b-%Y_%H-%M')
        response = HttpResponse(data, content_type="application/json")
        response['Content-Disposition'] = 'attachment; filename=%s' % file_label
        return response
    except:
        dest =  request.META.get('HTTP_REFERER', '/')
        messages.info(request, 'Fixture name not recognized: %s' % fixture)
        return HttpResponseRedirect(dest)
