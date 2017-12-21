import inspect
import importlib

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps as django_apps
from django.db import transaction

from accountifie.gl.bmo import BusinessModelObject
from accountifie.gl.models import TranLine
from accountifie.common.api import api_func

import logging
logger = logging.getLogger('default')


class Command(BaseCommand):

    help = 'Rebuild ALL general ledger entries'
    
    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        if verbosity > 0:
            print("Dropping general ledger and rebuilding all entries")

        """
        klasses = []
        kl_paths = api_func('environment', 'variable_list', 'BMO_MODULES')

        # find all the BMO classes
        for path in kl_paths:
            for name, kl in inspect.getmembers(importlib.import_module(path), inspect.isclass):
                if BusinessModelObject in kl.__bases__:
                    klasses.append(kl)

        
        with transaction.atomic():
            #quicker to do the two delets ourselves than let the engine work out all the cascading stuff
            TranLine.objects.all().delete()
        """

        for model in django_apps.get_models():
            if issubclass(model, BusinessModelObject):
                if verbosity > 0:
                    print("rebuilding GL entries from %s.%s" % (model._meta.app_label, model.__name__))

                with transaction.atomic():
                    for bmo in model.objects.all():
                        try:
                            bmo.save()
                        except:
                            logger.error('rebuild_postgres_gl: failed on %s' % bmo)
