from accountifie.cal import is_period_id
import datetime
from datetime import tzinfo
from dateutil.parser import parse

ZERO = datetime.timedelta(0)

# A UTC class.
class utc(tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO
utc = utc()

def utcnow():
    u = datetime.datetime.utcnow()
    return u.replace(tzinfo=utc)


def daterange(start, end, bus_days_only=True):
    dates = [start + datetime.timedelta(days=d) for d in range(0, (end - start).days + 1)]

    if bus_days_only:
        return [d for d in dates if d.weekday()<5]
    else:
        return dates


def start_of_period(period_id):
    pid = period_id
    assert is_period_id(pid)
    year = int(pid[0:4])
    if len(pid) > 5: 
        part2 = int(pid[5:])  #month, week, quarter
        sep = pid[4]
    else:
        part2 = None
        sep = 'Y'
    if sep == 'W':        
        import isoweek
        return isoweek.Week(year, part2).monday()
    elif sep == 'M':
        return datetime.date(year, part2, 1)
    elif sep == 'Q':
        month_id = (part2 - 1) * 3 + 1
        return datetime.date(year, month_id, 1)
    elif sep == 'H':
        return start_of_half(part2, year)
    elif sep == 'Y':
        return datetime.date(year, 1, 1)
    else:
        raise ValueError("Unexpected date identifier %s" % id)
    
def end_of_period(period_id):
    assert is_period_id(period_id)
    pid = period_id
    year = int(period_id[0:4])
    if len(pid) > 5: 
        part2 = int(pid[5:])  #month, week, quarter
        sep = pid[4]
    else:
        part2 = None
        sep = 'Y'
    if sep == 'W':        
        import isoweek
        return isoweek.Week(year, part2).sunday()
    elif sep == 'M':
        return end_of_month(part2, year)
    elif sep == 'Q':
        return end_of_quarter(part2, year)
    elif sep == 'H':
        return end_of_half(part2, year)
    elif sep == 'Y':
        return datetime.date(year, 12, 31)
    else:
        raise ValueError("Unexpected date identifier %s" % id)


##### END DOCENGINE  #####


from pandas.tseries.offsets import BDay
def prev_busday(d):
    if type(d) in [str, unicode]:
        d = parse(d).date()
    return (d - BDay(1)).date()


def as_date(thing):
    if isinstance(thing, datetime.date):
        return thing
    elif type(thing) == type(u''):
        if '-' in thing:
            y,m,d = thing.split('-')
            return datetime.date(int(y), int(m), int(d))
    raise ValueError("Cannot represent %s as date" % repr(thing))


def start_of_next_month(d):
    if not isinstance(d, datetime.date):
        raise ValueError('Unexpected date: %s' % repr(d))
    year = d.year
    month = d.month + 1
    if month == 13:
        month = 1
        year += 1
    return datetime.date(year, month, 1)


def start_of_year(yr):
    return datetime.date(yr, 1, 1)

def end_of_year(yr):
    return datetime.date(yr, 12, 31)

def end_of_prev_year(yr):
    return datetime.date(yr - 1, 12, 31)

def end_of_month(mth,yr):
    if mth==12:
        return datetime.date(yr+1,1,1) - datetime.timedelta(days=1)
    else:
        return datetime.date(yr,mth+1,1) - datetime.timedelta(days=1)

def end_of_months(yr):
    return [end_of_month(mth, yr) for mth in range(1,13)]


def end_of_prev_month(mth,yr):
    return datetime.date(yr,mth,1) - datetime.timedelta(days=1)

def start_of_month(mth,yr):
    return datetime.date(yr,mth,1)


def MTD(dt):
    return start_of_month(dt.month, dt,year), dt


def QTD(dt):
    mm = dt.month
    if mm <=3:
        qtr = 1
    elif mm <=6:
        qtr = 2
    elif mm <=9:
        qtr = 3
    else:
        qtr = 4
    
    return start_of_quarter(qtr, dt.year), dt

def HTD(dt):
    mm = dt.month
    if mm <=6:
        half = 1
    else:
        half = 2
    
    return start_of_half(half), dt


def start_of_quarter(qtr, yr):
    return datetime.date(yr, qtr*3 - 2, 1)

def end_of_quarter(qtr, yr):
    return end_of_month(qtr*3, yr)

def end_of_prev_quarter(qtr, yr):
    start_of_qtr = start_of_quarter(qtr, yr)
    return start_of_qtr + datetime.timedelta(days=-1)


def start_of_half(half, yr):
    return datetime.date(yr, half*6 - 5, 1)

def end_of_half(half, yr):
    return end_of_month(half*6, yr)

def end_of_prev_half(half, yr):
    return start_of_half(half, yr) + datetime.timedelta(days=-1)


def month_ends(yr):
    return [end_of_month(m, yr) for m in range(1,13)]

def monthrange(start, finish):
    months = (finish.year - start.year) * 12 + finish.month + 1
    for i in xrange(start.month, months):
        year  = (i - 1) / 12 + start.year
        month = (i - 1) % 12 + 1
        yield (year, month)
