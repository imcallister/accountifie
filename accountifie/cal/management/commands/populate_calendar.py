#command to populate calendar
import time
from datetime import date
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = 'Ensure calendar tables are populated between two dates'
    args = ''

    def handle(self, *app_labels, **options):
        verbose = False
        started = time.clock()
        from accountifie import cal
            
        from_date = None
        to_date = None
            
        cal.populate(from_date=from_date, to_date=to_date, verbose=verbose)
        finished = time.clock()
        print("populated calendar in %0.1f seconds" % (finished - started))


