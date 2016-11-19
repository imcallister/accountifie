
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


def semi_ends(half, year):
    columns = [datefuncs.end_of_prev_half(int(half), int(year)).isoformat(),
               '%dH%d' % (int(year), int(half)),
               datefuncs.end_of_half(int(half), int(year)).isoformat()
               ]

    prev_half, prev_half_yr = datefuncs.prev_half(half, year)

    column_titles = ['end of %dH%d' % (int(prev_half_yr), int(prev_half)),
                     'chg in %dH%d' % (int(year), int(half)),
                     'end of %dH%d' % (int(year), int(half))]
    return columns, column_titles


def quarter_ends(quarter, year):
    columns = [datefuncs.end_of_prev_quarter(int(quarter), int(year)).isoformat(),
               '%dQ%d' % (int(year), int(quarter)),
               datefuncs.end_of_quarter(int(quarter), int(year)).isoformat()
               ]

    prev_qtr, prev_qtr_yr = datefuncs.prev_quarter(quarter, year)

    column_titles = ['end of %dQ%d' % (int(prev_qtr_yr), int(prev_qtr)),
                     'chg in %dQ%d' % (int(year), int(quarter)),
                     'end of %dQ%d' % (int(year), int(quarter))]
    return columns, column_titles

def month_ends(month, year):
    month = int(month)
    year = int(year)
    columns = [datefuncs.end_of_prev_month(month, year).isoformat(),
               '%dM%s' % (year, '%02d' % month),
               datefuncs.end_of_month(month, year).isoformat()
               ]

    if month == 1:
        prev_mth = 12
        prev_yr = year - 1 
    else:
        prev_mth = month - 1
        prev_yr = year
    
    column_titles = ['end of %s %d' % (MONTHS[prev_mth-1], prev_yr),
                     'chg in %s %d' % (MONTHS[month-1], year),
                     'end of %s %d' % (MONTHS[month-1], year)]
    return columns, column_titles

