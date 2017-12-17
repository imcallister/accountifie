import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_models
from django.db import transaction

from accountifie.gl.bmo import BusinessModelObject
from accountifie.gl.models import Transaction, TranLine
from query.query_manager_strategy_factory import QueryManagerStrategyFactory

class Command(BaseCommand):

    help = 'Rebuild ALL general ledger entries'
    
    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        if verbosity > 0:
            print("Dropping general ledger and rebuilding all entries")

        with transaction.atomic():
            #quicker to do the two delets ourselves than let the engine work out all the cascading stuff
            TranLine.objects.all().delete()
            #Transaction.objects.all().delete()
            QueryManagerStrategyFactory().erase('*')


        QueryManagerStrategyFactory().set_fast_inserts('*', True)
        for model in get_models():
            
            if issubclass(model, BusinessModelObject):
                if verbosity > 0:
                    print("rebuilding GL entries from %s.%s" % (model._meta.app_label, model.__name__))
                with transaction.atomic():
                    for bmo in model.objects.all():
                        bmo.save()
        QueryManagerStrategyFactory().set_fast_inserts('*', False)
