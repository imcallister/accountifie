from . import gl_helpers

import datetime
import json



from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_DOWN
from bisect import insort
import locale
import operator
import re

import csv, os
from pprint import pprint

from django.db import models
from django.conf import settings

from . import datefuncs

locale.setlocale(locale.LC_ALL, '')



import logging
logger = logging.getLogger('default')


#use this frequently in rounding so give it a name
DZERO = Decimal("0.00")
HUNDREDTH = Decimal("0.01")

"""
def periods(period_tags):
    periods = {}
    for tag in period_tags:
        period_tag = period_tags[tag]
        periods[tag] = {'start': start_of_period(period_tag), 'end': end_of_period(period_tag)}
    return periods
"""

def day_before(d):
    return d - datetime.timedelta(days=1)

from pandas.tseries.offsets import BDay
def prev_busday(d):
    return (d - BDay(1)).date()


def entry(x, link='', ccy_fmt=''):
    return {'text': fmt(x, values_fmt=ccy_fmt), 'link': link}

def acct_history_link(id):
    from_dt = datefuncs.start_of_prev_year(datetime.datetime.now().year).isoformat()
    return ('/reporting/history/account/%s/?from=%s' % (id, from_dt))

def path_history_link(path):
    from_dt = datefuncs.start_of_prev_year(datetime.datetime.now().year).isoformat()
    return ('/reporting/history/path/%s/?from=%s' % (path.replace('.', '_'), from_dt))

def path_balances_link(path, date='today'):
    return ('/gl/path/%s/balances/?date=date' % path.replace('.','_'))

def fmt(stuff, values_fmt=None):
    "How do we want money formatted?"
    if stuff is None:
        return '----'
    elif isinstance(stuff, str):
        return stuff
    else:
        #accounting format, hacky, must be a recipe for this.
        #just seeing if brackets line up.
        if abs(stuff) < 0.1:
            txt = '-'
        elif stuff < 0:
            txt = '(' + locale.format("%0.0f", abs(stuff), grouping=True) + ')'
        else:
            txt = locale.format("%0.0f", stuff, grouping=True) + ''
        if values_fmt:
            return values_fmt + txt
        else:
            return txt

def unfmt(x):
    x = x.replace('$', '')
    if x == '-':
        return 0.0
    else:
        return float(x.replace(',','').replace(')','').replace('(','-'))





def get_dates(dt):
    if datefuncs.is_period_id(dt):
        start = datefuncs.start_of_period(dt)
        end = datefuncs.end_of_period(dt)
    elif type(dt) in [str, str] and dt[-4:]=='_YTD':
        end = parse(dt[:-4])
        start = datetime.date(end.year, 1, 1)
    elif type(dt) in [str, str] and dt[0] == 'D':
        d = parse(dt[1:]).date()
        start = prev_busday(d)+datetime.timedelta(days=1)
        end = d
    elif dt=='today':
        start = settings.DATE_EARLY
        end = datetime.datetime.now().date()
    else:
        start = settings.DATE_EARLY
        if type(dt)==str:
            end = parse(dt).date()
        else:
            end = dt
    return start, end

def get_dates_dict(dt):
    if type(dt)==dict:
        if 'start' in dt and 'end' in dt:
            #already in format
            return dt

    start, end = get_dates(dt)
    return { 'start': start, 'end': end }




def to_dict(dataset):
    "Make a dict with column 1 as key and cols 2,3,4 etc as value."
    d = {}
    for row in dataset:
        first, rest = row[0], row[1:]
        d[first] = rest
    return d

def denoneify(num):
    if num is None:
        return DZERO
    else:
        return num

def safe_sum(seq):
    "Safe with None"
    try:
        return sum(seq)
    except TypeError:
        seq2 = []
        for elem in seq:
            if elem is not None:
                seq2.append(elem)

        return sum(seq2)







def get_columns(request):
    if 'columns' in request.GET:
        return request.GET.get('columns').split('.')
    else:
        return None



def files_for_dir(datadir):
    return [os.path.join(datadir, name) for name in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, name))]

def csv_to_modelattr(open_file, name_cleaner=None, company=gl_helpers.get_default_company()):
    '''takes the fields and values in the CSV and transforms them into a list of dicts where the keys
     will match model attributes. for example Full Description becomes full_description'''
    if name_cleaner == None:
        name_cleaner = lambda name: name
    f_csv = csv.DictReader(open_file)
    csv_to_modelattr = dict([(name, name_cleaner(name)) for name in f_csv.fieldnames])
    csv_to_modelattr['company_id'] = company

    return [dict([(csv_to_modelattr[name], value) for name, value in list(row.items()) if name in csv_to_modelattr]) for row in f_csv]

def get_foreignkeys(model):
    return dict(((f.name, f.rel.to) for f in model._meta.fields if f.__class__ == models.ForeignKey))

def get_fk_attr(model):
    return [f.name for f in model._meta.fields if f.__class__ == models.ForeignKey]

def get_pk_name(model):
    return model._meta.pk.name

def instance_nonrel_data(row, model, name_cleaner=None, value_cleaner=None):
    model_flds =  model._meta.get_all_field_names()
    instance_data_no_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in list(row.items()) if name_cleaner(name)
                        and name_cleaner(name) not in get_fk_attr(model) and name_cleaner(name) in model_flds)
    return model(**instance_data_no_fk)

def set_foreignkeys(instance, row, model, name_cleaner=None, value_cleaner=None):
    if get_foreignkeys(model):
        instance_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in list(row.items()) if name_cleaner(name)
                        and name_cleaner(name) in get_fk_attr(model))
        for fk in list(get_foreignkeys(model).items()):
            if fk[0] in instance_fk:
                try:
                    related = fk[1].objects.get(pk=instance_fk[fk[0]])
                    setattr(instance, fk[0], related)
                except:
                    logger.error("No ForeignKey %s %s.  %s" % (fk[0], str(fk[1]), instance_fk))
    return instance

def dirty_key(row, model=None, unique=None, name_cleaner=None, value_cleaner=None):
    dirty = [name_cleaner(k) for k in list(row.keys())
                if name_cleaner(k) not in [f.name for f in [field for field in model._meta.fields
                        if field not in get_fk_attr(model)]]
                                if name_cleaner(k)]

    return dirty

def create_instance(row, model, name_cleaner=None, value_cleaner=None, unique=None, exclude=[], company=gl_helpers.get_default_company()):
    row['company'] = company
    non_rel_instance = instance_nonrel_data(row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)
    if non_rel_instance.id in exclude:
        return None

    full_instance = set_foreignkeys(non_rel_instance, row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)

    return unique(full_instance)


def random_color(dark=True):
    import random
    r = lambda: random.randrange(10,130 if dark else 255, 10)
    return '#%02X%02X%02X' % (r(),r(),r())
