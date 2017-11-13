"Re-saves all things which might produce GL transactions."
import logging
from dateutil.parser import parse
import datetime

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test

from accountifie.common.models import Log
from accountifie.celery import background_task
from accountifie.query.query_manager import QueryManager
from accountifie.gl.models import Company
from . import utils


logger = logging.getLogger('default')


def cleanlogs(request):
    try:
        clean_to = parse(request.GET['clean_to'])
    except:
        clean_to = datetime.datetime.now() + datetime.timedelta(days=1)
    
    task_name = 'cleanlogs'
    task_id = background_task(task=task_name, calc=_cleanlogs, clean_to=clean_to).id
    return HttpResponseRedirect('/tasks/list')


def _cleanlogs(*args, **kwargs):
    clean_to = kwargs['clean_to']
    to_clean = Log.objects.filter(time__lte=clean_to)
    Log.objects.filter(time__lte=clean_to).delete()
    logger.info('cleaned %d log entries to %s' %(len(to_clean), clean_to.isoformat()))
    return


@user_passes_test(lambda u: u.is_superuser)
def primecache(request):
    task_name = 'primecache'
    task_id = background_task(task=task_name, calc=_run_primecache)
    logger.info(request, 'Balances Cache primed')
    return HttpResponseRedirect('/tasks/list')  


def _run_primecache(*args, **kwargs):
    year = datetime.datetime.now().year
    dates_list = utils.end_of_months(year) + utils.end_of_months(year-1)
    dates = dict((dt.isoformat(), dt) for dt in dates_list)
    company_ids = [c['id'] for c in Company.objects.filter(cmpy_type='ALO').values('id')]
    tags = [None, ['yearend']]
    query_manager = QueryManager()
    for cmpy in company_ids:
        for tag in tags:
            exclude_cps = [None]
            exclude_cps.append([c for c in company_ids if c != cmpy])
            for exclude_cp in exclude_cps:
                logger.info('priming balance cache with %s, %s, %s' %(str(cmpy), str(tag), str(exclude_cp)))
                throw_away = query_manager.pd_acct_balances(cmpy, dates, excl_contra=exclude_cp, excl_tags=tag)
    return

