import datetime
from datetime import tzinfo
from dateutil.parser import parse
import isoweek
import re


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

UTC = utc()

def utcnow():
    u = datetime.datetime.utcnow()
    return u.replace(tzinfo=UTC)

def daterange(start, end, bus_days_only=True):
    dates = [start + datetime.timedelta(days=d) for d in range(0, (end - start).days + 1)]

    if bus_days_only:
        return [d for d in dates if d.weekday() < 5]
    else:
        return dates

def today():
    return datetime.datetime.now().date()

def yesterday():
    return prev_busday(today())


PAT_YEAR = re.compile("^\d{4}$")
PAT_MONTH = re.compile("^\d{4}M(0[1-9]{1}|10|11|12)$")
PAT_QUARTER = re.compile("^\d{4}Q[0-4]$")
PAT_HALF = re.compile("^\d{4}H[1-2]$")
PAT_WEEK = re.compile("^\d{4}W(0[1-9]|[1-4][0-9]|5[0-3]$)")
PAT_DAY = re.compile("^(D)(\d{4}-\d{1,2}-\d{1,2})")

#combine above 
PAT_PERIOD_ID = re.compile("|".join([PAT_YEAR.pattern, PAT_MONTH.pattern, PAT_QUARTER.pattern, PAT_HALF.pattern, PAT_WEEK.pattern, PAT_DAY.pattern]))


def is_period_id(text):
    if not text:
        return False

    match = PAT_PERIOD_ID.match(str(text))
    return (match is not None)


def start_of_period(period_id):
    pid = period_id
    assert is_period_id(pid)

    # daily
    if pid[0] == 'D':
        return prev_busday(parse(pid[1:]).date())

    year = int(pid[0:4])
    if len(pid) > 5: 
        part2 = int(pid[5:])  #month, week, quarter
        sep = pid[4]
    else:
        part2 = None
        sep = 'Y'
    if sep == 'W':        
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
    pid = period_id
    assert is_period_id(period_id)

    # daily
    if pid[0] == 'D':
        return parse(pid[1:]).date()


    year = int(period_id[0:4])
    if len(pid) > 5: 
        part2 = int(pid[5:])  #month, week, quarter
        sep = pid[4]
    else:
        part2 = None
        sep = 'Y'
    if sep == 'W':        
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

def end_of_prev_period(period_id):
    return start_of_period(period_id) - datetime.timedelta(days=1)

##### END DOCENGINE  #####


from pandas.tseries.offsets import BDay


def prev_busday(d):
    if type(d) in [str, str]:
        d = parse(d).date()
    return (d - BDay(1)).date()


def as_date(thing):
    if isinstance(thing, datetime.date):
        return thing
    elif type(thing) == type(''):
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
    return datetime.date(int(yr), 1, 1)

def start_of_prev_year(yr):
    return datetime.date(int(yr - 1), 1, 1)

def end_of_year(yr):
    return datetime.date(int(yr), 12, 31)

def end_of_prev_year(yr):
    return datetime.date(int(yr) - 1, 12, 31)

def end_of_month(mth,yr):
    mth = int(mth)
    yr = int(yr)
    if mth == 12:
        return datetime.date(int(yr) + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        return datetime.date(int(yr), int(mth) + 1, 1) - datetime.timedelta(days=1)

def end_of_months(yr):
    return [end_of_month(mth, yr) for mth in range(1,13)]


def end_of_prev_month(mth,yr):
    return datetime.date(int(yr), int(mth), 1) - datetime.timedelta(days=1)

def start_of_month(mth,yr):
    return datetime.date(int(yr), int(mth), 1)


def MTD(dt):
    return start_of_month(dt.month, dt.year), dt

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
    return datetime.date(int(yr), int(qtr) * 3 - 2, 1)

def end_of_quarter(qtr, yr):
    return end_of_month(int(qtr) * 3, int(yr))

def end_of_prev_quarter(qtr, yr):
    start_of_qtr = start_of_quarter(qtr, yr)
    return start_of_qtr + datetime.timedelta(days=-1)

def prev_quarter(qtr, year):
    qtr = int(qtr)
    year = int(year)
    if qtr == 1:
        return 4, year-1
    else:
        return qtr-1, year


def prev_half(half, year):
    half = int(half)
    year = int(year)
    if half == 1:
        return 2, year-1
    else:
        return 1, year

def start_of_half(half, yr):
    return datetime.date(int(yr), int(half) * 6 - 5, 1)

def end_of_half(half, yr):
    return end_of_month(int(half) * 6, int(yr))

def end_of_prev_half(half, yr):
    return start_of_half(half, yr) + datetime.timedelta(days=-1)


def month_ends(yr):
    return [end_of_month(m, yr) for m in range(1,13)]

def monthrange(start, finish):
    months = (finish.year - start.year) * 12 + finish.month + 1
    for i in range(start.month, months):
        year  = (i - 1) / 12 + start.year
        month = (i - 1) % 12 + 1
        yield (year, month)

def quarterrange(start, end):
    start_qtr = (start.year, (start.month -1)/3 + 1)
    end_qtr = (end.year, (end.month -1)/3 + 1)
    quarters = (end_qtr[0] - start_qtr[0]) * 4 + (end_qtr[1] - start_qtr[1]) + 1
    for i in range(start_qtr[1], start_qtr[1] + quarters):
        year  = (i - 1) / 4 + start.year
        qtr = (i - 1) % 4 + 1
        yield (year, qtr)

def halfrange(start, end):
    start_half = (start.year, (start.month -1)/6 + 1)
    end_half = (end.year, (end.month -1)/6 + 1)
    semis = (end_half[0] - start_half[0]) * 2 + (end_half[1] - start_half[1]) + 1
    for i in range(start_half[1], start_half[1] + semis):
        year  = (i - 1) / 2 + start.year
        half = (i - 1) % 2 + 1
        yield (year, half)


def annualrange(start, end):
    years = end.year - start.year + 1
    for year in range(start.year, start.year + years):
        yield year
