
import os, time, json
from optparse import make_option
from dateutil.parser import parse


from django.core.management.base import CommandError
from django.core.management.commands.startapp import Command as StartAppCommand
from django.core.exceptions import ObjectDoesNotExist
from accountifie.common.models import Log



class Command(StartAppCommand):
    option_list = StartAppCommand.option_list + (
        make_option('--clean_to',
                action='store', dest='clean_to',
                help='Date to which to clean logs'),
        )
                    
    def handle(self, app_name=None, target=None, **options):
        clean_to = parse(options.get('clean_to', None))
        Log.objects.filter(time__lte=clean_to).delete()