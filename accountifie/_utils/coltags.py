import re

from django.conf import settings

from datefuncs import *

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTH_TAG = re.compile("^\d{4}M(0[1-9]{1}|10|11|12)$")
QUARTER_TAG = re.compile("^\d{4}Q([1-4]{1})$")



def extractDateRange(request, inclusive=True):
    "Common notation to pull out to/from dates. Returns 2 date objects"

    if request.GET.has_key('year'):
        yyyy = int(request.GET.get('year'))
        from_date = datetime.date(yyyy, 1, 1)
        to_date = datetime.date(yyyy, 12, 31)
        if not inclusive:
            from_date = day_before(from_date)
    elif request.GET.has_key('month'):
        smonth = request.GET.get('month')
        syear, smonth = smonth.split('M')
        yyyy = int(syear)
        mm = int(smonth)
        from_date = datetime.date(yyyy, mm, 1)
        to_date = end_of_month(from_date.month, from_date.year)
        if not inclusive:
            from_date = day_before(from_date)
    elif request.GET.has_key('period'):
        period = request.GET.get('period')
        if period == 'YTD':
            yyyy = datetime.date.today().year
            from_date = datetime.date(yyyy, 1, 1)
            to_date = datetime.date.today()
            if not inclusive:
                from_date = day_before(from_date)

        elif period == 'QTD':
            yyyy = datetime.date.today().year
            mm = datetime.date.today().month
            if mm <=3:
                from_mm = 1
            elif mm <=6:
                from_mm = 4
            elif mm <=9:
                from_mm = 7
            else:
                from_mm = 10
            from_date = datetime.date(yyyy, from_mm, 1)
            to_date = datetime.date.today()
            if not inclusive:
                from_date = day_before(from_date)

        elif period == 'HTD':
            yyyy = datetime.date.today().year
            mm = datetime.date.today().month
            if mm <=6:
                from_mm = 1
            else:
                from_mm = 7
            from_date = datetime.date(yyyy, from_mm, 1)
            to_date = datetime.date.today()
            if not inclusive:
                from_date = day_before(from_date)
        elif period == 'MTD':
            yyyy = datetime.date.today().year
            mm = datetime.date.today().month
            from_date = datetime.date(yyyy, mm, 1)
            to_date = datetime.date.today()
            if not inclusive:
                from_date = day_before(from_date)

    else:
        from_date = as_date(request.GET.get('from', settings.DATE_EARLY))
        to_date = as_date(request.GET.get('to', settings.DATE_LATE))
    return from_date, to_date





def config_fromcoltag(col_tag, rpt_desc, calc_type):

    if col_tag[-9:] == 'Quarterly':
        yr = col_tag[:4]
        title = yr + ' ' + rpt_desc
        if calc_type == 'diff':
            columns = ['%sQ%d' % (yr, x) for x in range(1,5)]
            column_titles = ['Q1', 'Q2', 'Q3', 'Q4']
        elif calc_type == 'as_of':
            columns = [end_of_prev_year(int(yr)).isoformat(), yr, end_of_year(int(yr)).isoformat()]
            column_titles = ['end of %d' % (int(yr)-1), 'chg in %s' % yr, 'end of %s' % yr]
    elif col_tag[-6:] == 'Annual':
        yr = col_tag[:4]
        title = yr + ' ' + rpt_desc
        if calc_type == 'diff':
            columns = ['%s' % yr]
            column_titles = [str(yr)]
        elif calc_type == 'as_of':
            columns = [end_of_prev_year(int(yr)).isoformat(), yr, end_of_year(int(yr)).isoformat()]
            column_titles = ['end of %d' % (int(yr)-1), 'chg in %s' % yr, 'end of %s' % yr]
    elif col_tag[-7:] == 'Monthly':
        yr = col_tag[:4]
        # want to only show to end of current month
        #today = datetime.date.today()

        title = title = '%s for %s -- Monthly Detail' %(rpt_desc, yr)
        if calc_type == 'diff':
            
            columns = ['%sM%s' % (yr, '%02d' % x) for x in range(1,13)]
            column_titles = MONTHS
            
        elif calc_type == 'as_of':
            columns = [end_of_prev_year(int(yr))] + month_ends(int(yr))
            columns = [x.isoformat() for x in columns]
            column_titles = ['end of %d' % (int(yr)-1)] + MONTHS
    elif col_tag[:5] == 'daily':
        dt = parse(col_tag[6:]).date()

        columns = [prev_busday(dt), 'D%s' % dt.isoformat(), dt]
        column_titles = ['Yesterday', 'Change', 'Today']
        title = '%s for %s -- Daily view' %(rpt_desc, dt.isoformat())
    elif col_tag[-3:] == 'YTD':
        print col_tag
    elif col_tag[:3] == '5yr':
        dt = parse(col_tag[4:]).date()
        start = dt
        finish = datetime.date(start.year+5,start.month,start.day)

        months = list(monthrange(start, finish))

        title = '%s from %s -- 5yr view' %(rpt_desc, dt.isoformat())

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
