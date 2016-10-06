"Re-saves all things which might produce GL transactions."
import inspect
import importlib
import logging
import datetime

from django.db import transaction
from django.http import JsonResponse

from accountifie.gl.models import Transaction
from accountifie.gl.bmo import BusinessModelObject
from accountifie.common.api import api_func
from accountifie.celery import background_task
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory

logger = logging.getLogger('default')


def recalculate(request):
    task_name = 'ledger-recalculate-%s' % datetime.datetime.now().isoformat()
    task_id = background_task(task=task_name, calc=_recalculate).id
    status_url = 'background_task/status/%s' % task_id
    return JsonResponse({'task_id': task_id, 'task_name': task_name, 'status_url': status_url})


def _recalculate():
    klasses = []
    kl_paths = api_func('environment', 'variable_list', 'BMO_MODULES')

    # find all the BMO classes
    for path in kl_paths:
        for name, kl in inspect.getmembers(importlib.import_module(path), inspect.isclass):
            if BusinessModelObject in kl.__bases__:
                klasses.append(kl)

    with transaction.atomic():
        Transaction.objects.all().delete()

        for cmpny in [c['id'] for c in api_func('gl', 'company')]:
            QueryManagerStrategyFactory().erase(cmpny)

        logger.info("Recalculate -- deleted all transactions")
        QueryManagerStrategyFactory().set_fast_inserts('*', True)
        for klass in klasses:
            logger.info('Recalculate -- working on %s' % klass)
            qs =klass.objects.all()
            for obj in qs:
                obj.update_gl()
            logger.info('Recalculate -- finished %s' % klass)
        QueryManagerStrategyFactory().set_fast_inserts('*', False)
        QueryManagerStrategyFactory().take_snapshot('*')

    logger.info("Recalculate -- updated %d transactions" % qs.count())
    return
