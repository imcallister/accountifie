
import accountifie.toolkit.utils.datefuncs as datefuncs
import shortcuts

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def get_period_id(config):
    if config['period'] == 'year':
        return str(config['year'])
    elif config['period'] == 'half':
        return '%sH%s' % (config['year'], config['half'])
    elif config['period'] == 'quarter':
        return '%sQ%s' % (config['year'], config['quarter'])
    elif config['period'] == 'month':
        return '%sM%02d' % (config['year'], int(config['month']))
    elif config['period'] == 'day':
        return 'D%d-%02d-%02d' % (int(config['year']), int(config['month']), int(config['day']))
    else:
        raise ValueError("Bad config %s" % repr(config))


def monthly_periods(calc_type, start, end):
    months = list(datefuncs.monthrange(start, end))
    if calc_type == 'diff':
        columns = ['%sM%s' % (x[0], '%02d' % x[1]) for x in months]
        column_titles = ['%s %s' % (MONTHS[x[1]-1], x[0]) for x in months]    
    elif calc_type == 'as_of':
        columns = [datefuncs.end_of_month(x[1], x[0]).isoformat() for x in months]
        column_titles = columns
    else:
        raise ValueError("Bad calc_type %s" % repr(calc_type))
    
    return columns, column_titles

def quarterly_periods(calc_type, start, end):
    quarters = list(datefuncs.quarterrange(start, end))
    if calc_type == 'diff':
        columns = ['%sQ%s' % (x[0], '%0d' % x[1]) for x in quarters]
    elif calc_type == 'as_of':
        columns = [datefuncs.end_of_quarter(x[1], x[0]).isoformat() for x in quarters]
    else:
        raise ValueError("Bad calc_type %s" % repr(calc_type))
    
    column_titles = columns
    return columns, column_titles

def half_periods(calc_type, start, end):
    halfs = list(datefuncs.halfrange(start, end))
    if calc_type == 'diff':
        columns = ['%sH%s' % (x[0], '%0d' % x[1]) for x in halfs]
    elif calc_type == 'as_of':
        columns = [datefuncs.end_of_half(x[1], x[0]).isoformat() for x in halfs]
    else:
        raise ValueError("Bad calc_type %s" % repr(calc_type))
    
    column_titles = columns
    return columns, column_titles

def annual_periods(calc_type, start, end):
    years = list(datefuncs.annualrange(start, end))
    if calc_type == 'diff':
        columns = ['%s' % y  for y in years]
    elif calc_type == 'as_of':
        columns = [datefuncs.end_of_year(x).isoformat() for x in years]
    else:
        raise ValueError("Bad calc_type %s" % repr(calc_type))

    column_titles = columns
    return columns, column_titles

def day_periods(calc_type, start, end):
    columns = [start.isoformat(), end.isoformat()]
    column_titles = ['Previous Day', 'Current Day']
    return columns, column_titles

def gen_periods(calc_type, config):
    period_id = get_period_id(config)
    start = datefuncs.start_of_period(period_id)
    end = datefuncs.end_of_period(period_id)

    # if just as of end of single period... show chg
    if config['period'] == 'day':
        return single_period(config, start, end)

    if config['by'] == config['period'] and calc_type == 'as_of':
        return single_period(config, datefuncs.end_of_prev_period(period_id), end)

    if config['by'] == 'year':
        return annual_periods(calc_type, start, end)
    elif config['by'] == 'half':
        return half_periods(calc_type, start, end)
    elif config['by'] == 'quarter':
        return quarterly_periods(calc_type, start, end)
    elif config['by'] == 'month':
        return monthly_periods(calc_type, start, end)
    elif config['by'] == 'day':
        return day_periods(calc_type, start, end)
    else:
        raise ValueError("Unrecognised config %s" % repr(config))        


def daterange_periods(calc_type, config):
    start = shortcuts.date_from_shortcut(config['from'])
    end = shortcuts.date_from_shortcut(config['to'])
    
    if config['by'] == 'year':
        return annual_periods(calc_type, start, end)
    elif config['by'] == 'half':
        return half_periods(calc_type, start, end)
    elif config['by'] == 'quarter':
        return quarterly_periods(calc_type, start, end)
    elif config['by'] == 'month':
        return monthly_periods(calc_type, start, end)
    else:
        columns = [start.isoformat(), end.isoformat()]
        column_titles = list(columns)
        return columns, column_titles


# SINGLE PERIODS
def single_period(config, start, end):
    period_id = get_period_id(config)
    columns = [start.isoformat(), period_id, end.isoformat()]
    column_titles = [columns[0], 'chg in period', columns[2]]
    return columns, column_titles


