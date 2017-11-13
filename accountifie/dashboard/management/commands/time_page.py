"""
Adapted with permission from ReportLab's DocEngine framework
"""


import os
import sys
import time
import json 
import logging

from datetime import datetime
from optparse import make_option
try:
    from splinter import Browser
except:
    sys.stdout.write('You need to install splinter for this to run properly!!!\n')
    sys.exit(1)

from time import clock
from urllib.parse import urlparse

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

logger = logging.getLogger('default')

LOGS_DIR = os.path.realpath(os.path.join(settings.PROJECT_DIR, '..', 'logs'))

class Command(BaseCommand):
    """
    Logs the access time for a given URL as JSON under <repository>/logs/
    (defaults to http://www.reportlab.com/)
    filename will be made of the `slugify(last-10-chars-of-url)`.json
    """
    help = __doc__
    option_list = BaseCommand.option_list + (
        make_option("-u", "--url", 
            dest="url",
            help="The URL (with port) you want to test against",
            default="http://www.reportlab.com/"
            ),
        make_option("-b", "--browser", 
            dest="browser",
            help="Choose the browser: chrome or phantomjs", 
            default="phantomjs"
            ),
        make_option("-s", "--search", 
            dest="search",
            help="Search string to find in the content of the resulting page", 
            default=""
            ),
        make_option("-t", "--threshold", 
            dest="threshold",
            help="Last N log entries with go over the limit", 
            default=5
            ),
        make_option("-l", "--limit", 
            dest="limit",
            help="Time limit in seconds above which an error will be reported",
            default=5
            )
    )

    def handle(self, *args, **options):
        verbose = int( options['verbosity'])
        browser = options['browser']
        url = options.get('url', "http://www.reportlab.com/")
        search = options['search']
        limit = int(options['limit']*1000)
        threshold = int(options['threshold'])


        # naming sjon log upon the provided url
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        filename = os.path.join(LOGS_DIR, "%s.json" % slugify(url[-10:]).replace('-','_'))
        screenshotname = os.path.splitext(filename)[0]
            


        if '?' not in url and ('/media/' or '/static/' not in url) and not url.endswith('/'):
            url+='/'
        with Browser(browser) as b:
            for i in range(3):
                started = clock()
                b.visit(url)
                finished = time.clock()
                print('page visit in %0.3f seconds' % (finished - started))
            if not b.status_code.is_success:
                logging.error('[time_page] Request to %s returned an Error' % search)
                if verbose>1:
                    self.stdout.write('[time_page] Request to %s returned an Error' % search)
            if search and not search in b.html:
                logging.error('%s could not be found in the resulting page' % search)
                if verbose>1:
                    self.stdout.write('%s could not be found in the resulting page' % search)
                return 1
            
            how_long = int(1000 * (finished - started))
            if verbose > 1:
                print(('%0.2fms\n' % how_long))
                # sys.exit(1)
            if os.path.isfile(filename):
                with open(filename, 'r') as infile:
                    try:
                        log = json.load(infile)
                    except:
                        log = []
            else:
                log = []
            log.append({'when': datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
                    'how_long': how_long}
                    )
            with open(filename, 'w') as outfile:
                json.dump(log, outfile)

            last_ones = log[-threshold:]
            exceeds_limit = True 
            for i in last_ones:
                if i['how_long'] < threshold * 1000:
                    exceeds_limit = False
                    break
            if exceeds_limit:
                logger.error('Excessive loading time (>%sms) accessing url %s' % (limit, url))

