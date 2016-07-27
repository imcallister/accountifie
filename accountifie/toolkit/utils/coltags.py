import re

from django.conf import settings
from dateutil.parser import parse
from datefuncs import *
from make_config import *

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

MONTH_TAG = re.compile("^(\d{4})M(0[1-9]{1}|10|11|12)$")
QUARTER_TAG = re.compile("^(\d{4})Q([1-4]{1})$")
HALF_TAG = re.compile("^(\d{4})H([1-2]{1})$")
QUARTERLY_TAG = re.compile('(\d{4})(Quarterly)')
ANNUAL_TAG = re.compile('(\d{4})(Annual)')
MONTHLY_TAG = re.compile('(\d{4})(Monthly)')
DAILY_TAG = re.compile('(daily_)(\d{4}-\d{1,2}-\d{1,2})')
TRAILING12M_TAG = re.compile('(12Mtrailing)(-?)(\d{4}-\d{1,2}-\d{1,2})?')
MULTIYEAR_TAG = re.compile('(\d{1,2})yr_(\d{4}-\d{1,2}-\d{1,2})?')


def extractDateRange(request, inclusive=True):
    "Common notation to pull out to/from dates. Returns 2 date objects"

    if request.GET.has_key('year'):
        yyyy = int(request.GET.get('year'))
        from_date = start_of_year(yyyy)
        to_date = end_of_year(yyyy)
        if not inclusive:
            from_date = day_before(from_date)
    elif request.GET.has_key('month'):
        smonth = request.GET.get('month')
        syear, smonth = smonth.split('M')
        yyyy = int(syear)
        mm = int(smonth)
        from_date = start_of_month(mm, yyyy)
        to_date = end_of_month(mm, yyyy)
        if not inclusive:
            from_date = day_before(from_date)
    elif request.GET.has_key('period'):
        period = request.GET.get('period')
        if period == 'YTD':
            today = datetime.date.today()
            from_date = start_of_year(today.year)
            to_date = today
        elif period == 'QTD':
            from_date, to_date = QTD(datetime.date.today())
        elif period == 'HTD':
            from_date, to_date = HTD(datetime.date.today())
        elif period == 'MTD':
            from_date, to_date = MTD(datetime.date.today())
        
        if not inclusive:
                from_date = day_before(from_date)
    else:
        from_date = as_date(request.GET.get('from', settings.DATE_EARLY))
        to_date = as_date(request.GET.get('to', settings.DATE_LATE))
    return from_date, to_date


def config_fromcoltag(col_tag, rpt_desc, calc_type):

    # annual period by quarter... eg 2016Quarterly
    quarterly_match = QUARTERLY_TAG.search(col_tag)
    if quarterly_match:
        yr = quarterly_match.groups()[0]
        title = yr + ' ' + rpt_desc

        if calc_type == 'diff':
            columns, column_titles = quarterly_periods(yr)
        elif calc_type == 'as_of':
            columns, column_titles = quarter_ends(yr)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    annual_match = ANNUAL_TAG.search(col_tag)
    if annual_match:
        yr = annual_match.groups()[0]
        title = yr + ' ' + rpt_desc

        if calc_type == 'diff':
            columns, column_titles = annual_periods(yr)
        elif calc_type == 'as_of':
            columns, column_titles = annual_ends(yr)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    monthly_match = MONTHLY_TAG.search(col_tag)
    if monthly_match:
        yr = monthly_match.groups()[0]
        title = '%s for %s -- Monthly Detail' %(rpt_desc, yr)

        if calc_type == 'diff':
            columns, column_titles = monthly_periods(yr)
        elif calc_type == 'as_of':
            columns, column_titles = monthly_ends(yr)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    daily_match = DAILY_TAG.search(col_tag)
    if daily_match:
        dt = parse(daily_match.groups()[1]).date()
        title = '%s for %s -- Daily view' %(rpt_desc, dt.isoformat())
        columns = [prev_busday(dt), 'D%s' % dt.isoformat(), dt]
        column_titles = ['Yesterday', 'Change', 'Today']

        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    trailing12M_match = TRAILING12M_TAG.search(col_tag)
    if trailing12M_match:
        if trailing12M_match.groups()[2]:
            dt = parse(trailing12M_match.groups()[2]).date()
        else:
            dt = datetime.datetime.today().date()

        title = '%s from %s -- trailing 12mth' %(rpt_desc, dt.isoformat())
        if calc_type == 'diff':
            columns, column_titles = trailing_monthly_periods(dt)
        elif calc_type == 'as_of':
            columns, column_titles = trailing_monthly_ends(dt)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    multiyear_match = MULTIYEAR_TAG.search(col_tag)
    if multiyear_match:
        if multiyear_match.groups()[1]:
            dt = parse(multiyear_match.groups()[1]).date()
        else:
            dt = datetime.datetime.today().date()

        years = int(multiyear_match.groups()[0])

        title = '%s from %s -- %dyr view' %(rpt_desc, dt.isoformat(), years)
        if calc_type == 'diff':
            columns, column_titles = multiyear_periods(dt, years)
        elif calc_type == 'as_of':
            columns, column_titles = multiyear_ends(dt, years)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    month_tag = MONTH_TAG.match(col_tag)
    if month_tag is not None:
        yr = int(month_tag.groups()[0])
        mth = int(month_tag.groups()[1])
        tag_label = '%s %d' % (MONTHS[mth-1], yr)

        if calc_type == 'as_of':
            columns, column_titles = single_month_end(mth, yr, col_tag)
            title = '%s for %s' %(rpt_desc, tag_label)
        elif calc_type == 'diff':
            columns = [col_tag]
            column_titles = [tag_label]
            title ='%s for %s' %(rpt_desc, col_tag)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    quarter_tag = QUARTER_TAG.match(col_tag)
    if quarter_tag is not None:
        yr = int(quarter_tag.groups()[0])
        qtr = int(quarter_tag.groups()[1])

        tag_label = 'Q%s %d' % (qtr, yr)
        if calc_type == 'as_of':
            columns, column_titles = single_quarter_end(qtr, yr, col_tag)
            title = '%s for %s' %(rpt_desc, tag_label)
        elif calc_type == 'diff':
            columns = [col_tag]
            column_titles = [tag_label]
            title ='%s for %s' %(rpt_desc, col_tag)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}
    

    half_tag = HALF_TAG.search(col_tag)
    if half_tag:
        yr = int(half_tag.groups()[0])
        half = int(half_tag.groups()[1])
        tag_label = 'H%d %d' % (half, yr)

        if calc_type == 'as_of':
            columns, column_titles = single_half_end(half, yr, col_tag)
            title = '%s for %s' %(rpt_desc, tag_label)
        elif calc_type == 'diff':
            columns = [col_tag]
            column_titles = [tag_label]
            title ='%s for %s' %(rpt_desc, col_tag)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    """
        # didn't match anything
        raise ValueError('Unexpected col_tag: %s' % repr(col_tag))
    
    except:
        raise ValueError('Unexpected col_tag: %s' % repr(col_tag))
    """