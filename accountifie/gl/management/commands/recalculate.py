"Re-saves all things which might produce GL transactions."
import os, time
from optparse import make_option
import inspect
import importlib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from accountifie.gl.models import Transaction
from accountifie.gl.bmo import  BusinessModelObject
from accountifie.common.api import api_func

from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory


class Command(BaseCommand):

    """
    option_list = BaseCommand.option_list + (
        make_option('--all',
                action='store_true', 
                help='Full recalc of GL'),
        )
    """ 
    
    def handle(self, *args, **options):
        #faster and less likely to mess stuff up.

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
            
            print("deleted all transactions")
            QueryManagerStrategyFactory().set_fast_inserts('*', True)
            for klass in klasses:
                print('working on', klass)    
                qs =klass.objects.all()
                for obj in qs:
                    obj.update_gl()
                print('finished with', klass)    
            QueryManagerStrategyFactory().set_fast_inserts('*', False)
            QueryManagerStrategyFactory().take_snapshot('*')
        print("updated %d transactions" % qs.count())
