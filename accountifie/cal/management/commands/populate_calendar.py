#command to populate calendar
import time
from datetime import date
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    """
    option_list = BaseCommand.option_list + (
        make_option('--from', default=None, dest='from_date',
            help='Earliest date you want in your calendar (YYYYMMDD, defaults to 1st of this year)'),
        make_option('--to', default=None, dest='to_date', 
            help='Latest date you want in your calendar (YYYYMMDD, defaults to last of this year)'),
        make_option('--delete', action="store_true", dest='delete', 
            help='empty the entire calendar'),

    )
    """
    help = 'Ensure calendar tables are populated between two dates'
    args = ''

    def handle(self, *app_labels, **options):
        verbose = (int(options['verbosity']) > 1)
        started = time.clock()
        from accountifie import cal
            

        if options['delete']:
            from accountifie.cal.models import Year, Quarter, Month, Week, Day
            if verbose: print("deleting all calendar entries...")
            for klass in [Day, Week, Month, Quarter, Year]:
                klass.objects.all().delete()
            if verbose: print("done.")


        from_date = options['from_date']
        if from_date is not None:
            yyyy = int(from_date[0:4])
            mm = int(from_date[4:6])
            dd = int(from_date[6:8])
            print yyyy,mm,dd
            from_date = date(yyyy, mm, dd)
            
        to_date = options['to_date']
        if to_date is not None:
            yyyy = int(to_date[0:4])
            mm = int(to_date[4:6])
            dd = int(to_date[6:8])
            to_date = date(yyyy, mm, dd)
            
        cal.populate(from_date=from_date, to_date=to_date, verbose=verbose)
        finished = time.clock()
        print "populated calendar in %0.1f seconds" % (finished - started)


