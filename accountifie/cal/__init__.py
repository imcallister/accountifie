"""Calendar module as recommended by Celko.

We have pre-joined database records for Year, Quarter,
Month and Day objects.  This means that if one needs
to total sales by quarter, or to make screens to
browse through VAT quarters or statements, it can be
done very efficiently in SQL.

MySQL date functions are good enough to group by end-of-month,
but other entities in an accounts system can often be of a
monthly or quarterly nature, so find it easy to have a
month_id or quarter_id.

Years are identified as '2009', quarters as '2009Q1'
and months as '2009M07' to ensure alpha order equals chrono
order.

The populate function can be called on startup to ensure
it is always populated for the current year; and also
from
   manage.py populate_calendar --from=YYYYMMDD --to=YYYYMMDD





"""
import re
from datetime import date, timedelta, datetime
from django.db import transaction

#for quick checking if we have a valid period id.  Does not rule out e.g. week 59 or month 19;-)
PAT_YEAR = re.compile("^\d{4}$")
PAT_MONTH = re.compile("^\d{4}M(0[1-9]{1}|10|11|12)$")
PAT_QUARTER = re.compile("^\d{4}Q[0-4]$")
PAT_HALF = re.compile("^\d{4}H[1-2]$")
PAT_WEEK = re.compile("^\d{4}W(0[1-9]|[1-4][0-9]|5[0-3]$)")
PAT_DAY = re.compile("^(D)(\d{4}-\d{1,2}-\d{1,2})")

#combine above 
PAT_PERIOD_ID = re.compile("|".join([PAT_YEAR.pattern, PAT_MONTH.pattern, PAT_QUARTER.pattern, PAT_HALF.pattern, PAT_WEEK.pattern, PAT_DAY.pattern]))


@transaction.atomic
def populate(from_date=None,
             to_date=None,
             verbose=False):
    """Ensure calendar has all dates in the range.
    """
    if not from_date:
        now = date.today()
        from_date = date(now.year, 1, 1)
    if not to_date:
        now = date.today()
        next_new_year = date(now.year + 1, 1, 1)
        to_date = next_new_year - timedelta(1)


    from .models import Day, Month, Quarter, Year, Week
    
    #quick check to make this cheap to run on startup.  
    days = (to_date - from_date).days + 1
    already = Day.objects.filter(id__gte=from_date, id__lte=to_date).count()
    if days == already:
        print("Already populated")
        return

    #get all the records for efficiency so we can create
    #anything missing

    days = dict((day.id, day) for day in Day.objects.all())
    months = dict((month.id, month) for month in Month.objects.all())
    quarters = dict((qtr.id, qtr) for qtr in Quarter.objects.all())
    years = dict((year.id, year) for year in Year.objects.all())
    
    
    if verbose:
        print('populating calendar from %s to %s' % (from_date, to_date))
    d = from_date
    while d <= to_date:
        year_id = d.year
        quarter_num = ((d.month-1)/3)+1
        quarter_id = '%04dQ%01d' % (d.year, quarter_num)
        month_id = '%04dM%02d' % (d.year, d.month)

        #find or create the Year object
        if year_id not in years:
            djyear = Year(id=d.year)
            djyear.save()
            years[d.year] = djyear
            if verbose: print('    added year %s' % d.year)
        else:
            djyear = years[year_id]
            
        #find or create the Quarter object
        if quarter_id not in quarters:
            djquarter = Quarter(id=quarter_id, year=djyear)
            djquarter.save()
            quarters[quarter_id] = djquarter
            if verbose: print('        added quarter %s' % quarter_id)
        else:
            djquarter = quarters[quarter_id]
        
        #find or create the Month object
        if month_id not in months:
            djmonth = Month(id=month_id,
                            year=djyear,
                            quarter=djquarter)
            djmonth.save()
            months[month_id] = djmonth
            if verbose: print('            added month %s' % month_id)
        else:
            djmonth = months[month_id]
        
        #find or create the Day object
        if d not in days:
            djday = Day(id=d,
                        year=djyear,
                        quarter=djquarter,
                        month=djmonth)
            djday.save()
            days[d] = djday
            if verbose: print('              added day %s' % d)
        
        d = d + timedelta(1)


    #now for the weeks
    d = from_date
    #roll backwards to monday, in case of an incomplete one from last year
    while d.weekday() != 0:
        d = d - timedelta(days=1)

    while d <= to_date:
        yyyy, wk, wkday = d.isocalendar()
        week_id = '%04dW%02d' % (yyyy, wk)
        try:
            week = Week.objects.get(id=week_id)
        except Week.DoesNotExist:
            week = Week(id=week_id)
            week.year_id = yyyy
            week.first_day = d
            week.last_day = d + timedelta(days=6)
            #join up all the joins.
            
            try:
                week.start_month = Month.objects.get(id="%04dM%02d" % (yyyy, d.month))
                week.end_month = Month.objects.get(id="%04dM%02d" % (yyyy, d.month))
                week.save()
                if verbose: print(("created week %s" % week_id))
            except Month.DoesNotExist:
                #hit year end, don't bother saving this week
                if verbose: print(("No related month, skipping %s" % week_id))
                
        d = d + timedelta(days=7)



    return



def start_of_month(d):
    return date(d.year, d.month, 1)

def end_of_month(d):
    year = d.year
    month = d.month + 1
    if month > 12:
        year += 1
        month = 1
    return date(year, month, 1) - timedelta(days=1)

def end_of_previous_month(d):
    return start_of_month(d) - timedelta(days=1)


#brute force depending on month index, gives month-year for each input month
_QUARTER_RANGES = [
    (None,None),  #no month zero
    (1,1,3,31),
    (1,1,3,31), 
    (1,1,3,31), 
    (4,1,6,30),
    (4,1,6,30), 
    (4,1,6,30), 
    (7,1,9,30),
    (7,1,9,30), 
    (7,1,9,30), 
    (10,1,12,31),
    (10,1,12,31),   
    (10,1,12,31),   
    ]   

def start_of_quarter(dt):
    a,b,c,d = _QUARTER_RANGES[dt.month]
    return date(dt.year, a, b)

def end_of_quarter(dt):
    a,b,c,d = _QUARTER_RANGES[dt.month]
    return date(dt.year, c, d)

def start_of_half(dt):
    if dt.month < 7:
        return date(dt.year, 1, 1)
    else:
        return date(dt.year, 6, 1)

def end_of_half(dt):
    if dt.month < 7:
        return date(dt.year, 6, 30)
    else:
        return date(dt.year, 12, 31)


def start_of_year(dt):  
    return date(dt.year, 1, 1)

def end_of_year(dt):    
    return date(dt.year, 12, 31)

def start_of_week(dt):
    year, week, weekday = dt.isocalendar()
    return dt - timedelta(days=weekday-1)

def end_of_week(dt):
    year, week, weekday = dt.isocalendar()
    return dt + timedelta(days=(7-weekday))


def is_period_id(text):
    if not text:
        return False

    match = PAT_PERIOD_ID.match(str(text))
    return (match is not None)


def is_iso_date(text):
    try:
        return datetime.strptime(text, '%Y-%M-%d')
    except ValueError:
        return False

def parse_iso_date(text):
    if isinstance(text, datetime.date):
        return text
    return datetime.strptime(text, '%Y-%M-%d')

def this_quarter_id():
    "Returns quarter identifier for present"
    t = date.today()
    q = int((t.month + 1)/3)
    return '%04dQ%d' % (t.year, q)

def this_half_id():
    "Returns half identifier for present"
    t = date.today()
    if t.month < 7:
        half = 1
    else:
        half = 2
    return '%04dH%d' % (t.year, half)

def this_month_id():
    "Returns month identifier for present"
    t = date.today()
    return '%04dM%02d' % (t.year, t.month)
    

def this_week_id():
    "Returns week identifier for present"
    y, w, wd = date.today().isocalendar()
    return '%04dW%02d' % (y, w)
    

def tofirstdayinisoweek(year, week):
    #from stackoverflow
    ret = strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if date(year, 1, 4).isoweekday() > 4:
        ret -= timedelta(days=7)
    return ret

def previous_period(id):
    "Returns identifier for preceding period"
    year = int(id[0:4])
    part2 = int(id[5:])  #month, week, quarter
    if id[4] == 'W':
        import isoweek
        monday = isoweek.Week(year, part2).monday()
        previous_monday = monday - timedelta(days=7)
        y,w,wd = previous_monday.isocalendar()
        return '%04dW%02d' % (y, w)
    elif id[4] == 'M':
        part2 = part2 - 1
        if part2 == 0:
            part2 = 12
            year -= 1
        return '%04dM%02d' % (year, part2)
    elif id[4] == 'Q':
        part2 = part2 - 1
        if part2 == 0:
            part2 = 4
            year -= 1
        return '%04dQ%01d' % (year, part2)
    elif id[4] == 'H':
        if part2 == 1:
            year -= 1
            half = 2
        else:
            half = 1
        return '%04dH%01d' % (year, half)
    else:
        raise ValueError("Unexpected date identifier %s" % id)


def next_period(id):
    "Returns identifier for next period"
    year = int(id[0:4])
    part2 = int(id[5:])  #month, week, quarter
    if id[4] == 'W':        
        import isoweek
        monday = isoweek.Week(year, part2).monday()
        next_monday = monday + timedelta(days=7)
        y,w,wd = next_monday.isocalendar()
        return '%04dW%02d' % (y, w)
    elif id[4] == 'M':
        part2 = part2 + 1
        if part2 == 13:
            part2 = 1
            year += 1
        return '%04dM%02d' % (year, part2)
    elif id[4] == 'Q':
        part2 = part2 + 1
        if part2 == 5:
            part2 = 1
            year += 1
        return '%04dQ%01d' % (year, part2)
    elif id[4] == 'H':
        if part2 == 2:
            year += 1
            half = 1
        else:
            half = 2
        return '%04dH%01d' % (year, half)

    else:
        raise ValueError("Unexpected date identifier %s" % id)


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
        return date(year, part2, 1)
    elif sep == 'Q':
        month_id = (part2 - 1) * 3 + 1
        return date(year, month_id, 1)
    elif sep == 'H':
        return start_of_half(date(year, (part2*6), 1))
    elif sep == 'Y':
        return date(year, 1, 1)
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
        return end_of_month(date(year, part2, 1))
    elif sep == 'Q':
        return end_of_quarter(date(year, (part2*3), 1))
    elif sep == 'H':
        return end_of_half(date(year, (part2*6), 1))
    elif sep == 'Y':
        return date(year, 12, 31)
    else:
        raise ValueError("Unexpected date identifier %s" % id)





def supply_date_context():
    """Supply a dictionary with stuff for time navigation in templates

    Contains string IDs for everything so you can build URLs.
    """
    #array we can index into with 1..12
    MONTHNAMES = [None] + "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    d = {}
    today = date.today()
    d['today'] = today.isoformat()
    d['tomorrow'] = (today + timedelta(days=1)).isoformat()
    d['yesterday'] = (today - timedelta(days=1)).isoformat()

    d['this_year'] = str(today.year)
    d['last_year'] = str(today.year - 1)
    d['next_year'] = str(today.year + 1)

    d['this_quarter'] = this_quarter_id()
    d['next_quarter'] = next_period(d['this_quarter'])
    d['last_quarter'] = previous_period(d['this_quarter'])
    d['two_quarters_ago'] = previous_period(d['last_quarter'])

    d['this_month'] = this_month_id()
    d['next_month'] = next_period(d['this_month'])
    d['last_month'] = previous_period(d['this_month'])
    d['two_months_ago'] = previous_period(d['last_month'])

    d['this_month_mmm'] = MONTHNAMES[today.month]
    last_month = end_of_previous_month(today)
    d['last_month_mmm'] = MONTHNAMES[last_month.month]
    two_months_ago = end_of_previous_month(last_month)
    d['two_months_ago_mmm'] = MONTHNAMES[two_months_ago.month]

    d['this_week'] = this_week_id()
    d['next_week'] = next_period(d['this_week'])
    d['last_week'] = previous_period(d['this_week'])
    d['two_weeks_ago'] = previous_period(d['last_week'])

    return d


if __name__=='__main__':
    populate()
