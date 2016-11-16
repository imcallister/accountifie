import datetime

import accountifie.toolkit.utils.datefuncs as datefuncs


MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def annual_periods(year):
    columns = ['%s' % year]
    column_titles = [str(year)]
    return columns, column_titles

def annual_ends(year):
    columns = [datefuncs.end_of_prev_year(int(year)).isoformat(), year, datefuncs.end_of_year(int(year)).isoformat()]
    column_titles = ['end of %d' % (int(year)-1), 'chg in %s' % year, 'end of %s' % year]
    return columns, column_titles



def half_periods(year):
    columns = ['%sH%d' % (year, x) for x in range(1,3)]
    column_titles = ['H1', 'H2']
    return columns, column_titles

def half_ends(year):
    columns = [datefuncs.end_of_prev_year(int(year)).isoformat()]
    column_titles = ['end of %d' % (int(year)-1)]

    for h in [1,2]:
        columns.append(datefuncs.end_of_half(h, int(year)).isoformat())
        column_titles.append('end of H%d' % h)
    return columns, column_titles


def quarterly_periods(year):
    columns = ['%sQ%d' % (year, x) for x in range(1,5)]
    column_titles = ['Q1', 'Q2', 'Q3', 'Q4']
    return columns, column_titles

def quarter_ends(year):
    columns = [datefuncs.end_of_prev_year(int(year)).isoformat()]
    column_titles = ['end of %d' % (int(year)-1)]

    for q in [1,2,3,4]:
        columns.append(datefuncs.end_of_quarter(q, int(year)).isoformat())
        column_titles.append('end of Q%d' %q)
    
    return columns, column_titles


def monthly_periods(year):
    columns = ['%sM%s' % (year, '%02d' % x) for x in range(1,13)]
    column_titles = MONTHS        
    return columns, column_titles

def monthly_ends(year):
    columns = [datefuncs.end_of_prev_year(int(year))] + datefuncs.month_ends(int(year))
    columns = [x.isoformat() for x in columns]
    column_titles = ['end of %d' % (int(year)-1)] + MONTHS
    return columns, column_titles




def gen_monthly_periods(start, end):
    months = list(datefuncs.monthrange(start, end))
    columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
    column_titles = ['%s %s' % (MONTHS[x[1]-1], x[0]) for x in months]    
    return columns, column_titles

def gen_monthly_ends(start, end):
    months = list(datefuncs.monthrange(start, end))
    columns = [datefuncs.end_of_month(x[1], x[0]).isoformat() for x in months]
    column_titles = columns
    return columns, column_titles

def gen_quarterly_periods(start, end):
    quarters = list(datefuncs.quarterrange(start, end))
    columns = ['%sQ%s' % (x[0], '%0d' % x[1]) for x in quarters]
    column_titles = columns
    return columns, column_titles

def gen_quarterly_ends(start, end):
    quarters = list(datefuncs.quarterrange(start, end))
    columns = [datefuncs.end_of_quarter(x[1], x[0]).isoformat() for x in quarters]
    column_titles = columns
    return columns, column_titles


def gen_semi_periods(start, end):
    semis = list(datefuncs.semirange(start, end))
    columns = ['%sH%s' % (x[0], '%0d' % x[1]) for x in semis]
    column_titles = columns
    return columns, column_titles

def gen_semi_ends(start, end):
    semis = list(datefuncs.semirange(start, end))
    columns = [datefuncs.end_of_half(x[1], x[0]).isoformat() for x in semis]
    column_titles = columns
    return columns, column_titles

def gen_annual_periods(start, end):
    years = list(datefuncs.annualrange(start, end))
    columns = ['%s' % y  for y in years]
    column_titles = columns
    return columns, column_titles


def gen_annual_ends(start, end):
    years = list(datefuncs.annualrange(start, end))
    columns = [datefuncs.end_of_year(x[1], x[0]).isoformat() for x in years]
    column_titles = columns
    return columns, column_titles


def single_month_end(month, year, col_tag):
    tag_label = '%s %d' % (MONTHS[month-1], year)
    
    end_of_this_month = datefuncs.end_of_month(month,year)
    end_of_prev_month = datefuncs.end_of_prev_month(month,year)
    
    columns = [end_of_prev_month.isoformat(), col_tag, end_of_this_month.isoformat()]
    column_titles = [end_of_prev_month.isoformat(), tag_label, end_of_this_month.isoformat()]
    return columns, column_titles
                
def single_quarter_end(quarter, year, col_tag):
    tag_label = 'Q%s %d' % (quarter, year)
    
    end_of_this_qtr = datefuncs.end_of_quarter(quarter,year)
    end_of_prev_qtr = datefuncs.end_of_prev_quarter(quarter,year)
    
    columns = [end_of_prev_qtr.isoformat(), col_tag, end_of_this_qtr.isoformat()]
    column_titles = [end_of_prev_qtr.isoformat(), tag_label, end_of_this_qtr.isoformat()]
    return columns, column_titles
    
def single_half_end(half, year, col_tag):
    tag_label = 'H%s %d' % (half, year)
    
    end_of_this_half = datefuncs.end_of_half(half,year)
    end_of_prev_half = datefuncs.end_of_prev_half(half,year)
    
    columns = [end_of_prev_half.isoformat(), col_tag, end_of_this_half.isoformat()]
    column_titles = [end_of_prev_half.isoformat(), tag_label, end_of_this_half.isoformat()]
    return columns, column_titles





def ytd_ends(dt, year):
    columns = [datefuncs.end_of_prev_year(int(year)).isoformat(), year, dt.isoformat()]
    column_titles = ['end of %d' % (int(year)-1), 'chg in %s' % year, 'End of Period']
    return columns, column_titles



def trailing_monthly_periods(dt):
    start = datetime.date(dt.year-1,dt.month,1)
    finish = dt

    months = list(datefuncs.monthrange(start, finish))
    columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
    column_titles = columns
    
    return columns, column_titles

def trailing_monthly_ends(dt):
    start = datetime.date(dt.year-1,dt.month,1)
    finish = dt

    months = list(datefuncs.monthrange(start, finish))
    columns = [datefuncs.end_of_month(x[1],x[0]).isoformat() for x in months]
    column_titles = columns  
    
    return columns, column_titles

def multiyear_periods(dt, years):
    start = datefuncs.start_of_month(dt.month, dt.year)
    finish = datetime.date(start.year + years, start.month, start.day)

    months = list(datefuncs.monthrange(start, finish))

    columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
    column_titles = columns

    return columns, column_titles
    
def multiyear_ends(dt, years):
    start = datefuncs.start_of_month(dt.month, dt.year)
    finish = datetime.date(start.year + years, start.month, start.day)

    months = list(datefuncs.monthrange(start, finish))

    columns = [datefuncs.end_of_month(x[1],x[0]).isoformat() for x in months]
    column_titles = columns

    return columns, column_titles
