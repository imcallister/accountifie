import re

from django.conf import settings
from dateutil.parser import parse
from datefuncs import *
from make_config import *

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTH_TAG = re.compile("^\d{4}M(0[1-9]{1}|10|11|12)$")
QUARTER_TAG = re.compile("^\d{4}Q([1-4]{1})$")
QUARTERLY_TAG = re.compile('(\d{4})(Quarterly)')
ANNUAL_TAG = re.compile('(\d{4})(Annual)')
MONTHLY_TAG = re.compile('(\d{4})(Monthly)')



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


    if col_tag[:5] == 'daily':
        dt = parse(col_tag[6:]).date()

        columns = [prev_busday(dt), 'D%s' % dt.isoformat(), dt]
        column_titles = ['Yesterday', 'Change', 'Today']
        title = '%s for %s -- Daily view' %(rpt_desc, dt.isoformat())
    elif col_tag[-3:] == 'YTD':
        print col_tag
    elif col_tag[:11] == '12Mtrailing':
        if col_tag[12:]=='':
            dt = datetime.datetime.today().date()
        else:
            dt = parse(col_tag[12:]).date()

        next_month = start_of_next_month(dt)
        start = datetime.date(dt.year-1,dt.month,1)
        finish = dt

        months = list(monthrange(start, finish))
        title = '%s from %s -- trailing 12mth' %(rpt_desc, dt.isoformat())

        if calc_type == 'diff':
            columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
            column_titles = columns
        elif calc_type == 'as_of':
            columns = [end_of_month(x[1],x[0]).isoformat() for x in months]
            column_titles = columns  
    elif col_tag[:3] == '4yr':
        dt = parse(col_tag[4:]).date()
        start = dt
        finish = datetime.date(start.year+4,start.month,start.day)

        months = list(monthrange(start, finish))

        title = '%s from %s -- 4yr view' %(rpt_desc, dt.isoformat())

        if calc_type == 'diff':
            columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
            column_titles = columns
        elif calc_type == 'as_of':
            columns = [end_of_month(x[1],x[0]).isoformat() for x in months]
            column_titles = columns
            # this logic doesn't really work for forecasts ... scratch it for now
    elif col_tag[:3] == '3yr':
        dt = parse(col_tag[4:]).date()
        start = dt
        finish = datetime.date(start.year+3,start.month,start.day)

        months = list(monthrange(start, finish))

        title = '%s from %s -- 3yr view' %(rpt_desc, dt.isoformat())

        if calc_type == 'diff':
            columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
            column_titles = columns
        elif calc_type == 'as_of':
            columns = [end_of_month(x[1],x[0]).isoformat() for x in months]
            column_titles = columns
            # this logic doesn't really work for forecasts ... scratch it for now
    
    else:
        try:
            columns = [col_tag]
            column_titles = [col_tag]

            if MONTH_TAG.match(col_tag) is not None:
                yr, month =  int(col_tag.split('M')[0]), int(col_tag.split('M')[1])
                tag_label = '%s %d' % (MONTHS[month-1], yr)
                if calc_type == 'as_of':
                    end_of_this_month = end_of_month(month,yr)
                    end_of_prev_month = start_of_month(month, yr) - datetime.timedelta(days=1)
                    columns = [end_of_prev_month.isoformat(), col_tag, end_of_this_month.isoformat()]
                    column_titles = [end_of_prev_month.isoformat(), tag_label, end_of_this_month.isoformat()]

                    title = '%s for %s' %(rpt_desc, tag_label)
                else:
                    columns = [col_tag]
                    column_titles = [tag_label]
                    title_date = datetime.date(yr,month,1).strftime('%B, %Y')
                    title ='%s for %s' %(rpt_desc, title_date)

            elif QUARTER_TAG.match(col_tag) is not None:
                yr, qtr =  int(col_tag.split('Q')[0]), int(col_tag.split('Q')[1])
                tag_label = 'Q%s %d' % (qtr, yr)
                if calc_type == 'as_of':
                    end_of_this_qtr = end_of_quarter(qtr, yr)
                    end_of_prev_qtr = start_of_quarter(qtr, yr) - datetime.timedelta(days=1)
                    columns = [end_of_prev_qtr.isoformat(), col_tag, end_of_this_qtr.isoformat()]
                    column_titles = [end_of_prev_qtr.isoformat(), tag_label, end_of_this_qtr.isoformat()]
                    title = '%s for %s' %(rpt_desc, tag_label)
                else:
                    columns = [col_tag]
                    column_titles = [tag_label]
                    title_date = datetime.date(yr,month,1).strftime('%B, %Y')
                    title ='%s for %s' %(rpt_desc, title_date)
            else:
                title = col_tag
        except:
            raise ValueError('Unexpected col_tag: %s' % repr(col_tag))


    return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}
