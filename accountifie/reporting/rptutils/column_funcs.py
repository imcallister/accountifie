
import accountifie.toolkit.utils.datefuncs as datefuncs


MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


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
    columns = [datefuncs.end_of_year(x).isoformat() for x in years]
    column_titles = columns
    return columns, column_titles


def annual_ends(year):
    columns = [datefuncs.end_of_prev_year(int(year)).isoformat(), year, datefuncs.end_of_year(int(year)).isoformat()]
    column_titles = ['end of %d' % (int(year)-1), 'chg in %s' % year, 'end of %s' % year]
    return columns, column_titles
