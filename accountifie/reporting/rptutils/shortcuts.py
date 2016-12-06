import re
import datetime

from django.conf import settings
from dateutil.parser import parse
import accountifie.toolkit.utils.datefuncs as datefuncs


MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

MONTH_TAG = re.compile("^(\d{4})M(0[1-9]{1}|10|11|12)(Monthly)?$")
QUARTER_TAG = re.compile("^(\d{4})Q([1-4]{1})(Quarterly|Monthly)?$")
HALF_TAG = re.compile("^(\d{4})H([1-2]{1})(Semi|Quarterly|Monthly)?$")
YEAR_TAG = re.compile("^(\d{4})(Annual|Semi|Quarterly|Monthly)?$")


YTD_TAG = re.compile('(YTD_)(\d{4}-\d{1,2}-\d{1,2})(Annual|Semi|Quarterly|Monthly)?')
DAILY_TAG = re.compile('(daily_)(\d{4}-\d{1,2}-\d{1,2})')
DAY_TAG = re.compile('(day_)(\d{4}-\d{1,2}-\d{1,2})')
TRAILING12M_TAG = re.compile('(12Mtrailing)(-?)(\d{4}-\d{1,2}-\d{1,2})?')
MULTIYEAR_TAG = re.compile('(\d{1,2})yr_(\d{4}-\d{1,2}-\d{1,2})(Annual|Semi|Quarterly|Monthly)?')


BY_MAP = {'Monthly': 'month',
          'Quarterly': 'quarter',
          'Semi': 'half',
          'Annual': 'year'}


def date_from_shortcut(scut):
    if not scut:
        return None
    
    if scut == 'yesterday':
        return datefuncs.yesterday()
    elif scut == 'today':
        return datefuncs.today()
    elif scut == 'end_of_last_month':
        today = datefuncs.today()
        return datefuncs.end_of_prev_month(today.month, today.year)
    elif scut is None:
        return datefuncs.today()
    else:
        try:
            if type(scut) == datetime.date:
                return scut
            elif type(scut) in [unicode, str]:
                return parse(scut).date()
            else:
                return
        except:
            return


def parse_shortcut(col_tag):

    day_tag = DAY_TAG.match(col_tag)
    if day_tag is not None:
        dt = parse(day_tag.groups()[1]).date()
        return {'config_type': 'period',
                'period': 'day', 
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
                'by': 'day'}

    month_tag = MONTH_TAG.match(col_tag)
    if month_tag is not None:
        year = month_tag.groups()[0]
        month = month_tag.groups()[1]
        return {'config_type': 'period',
                'period': 'month', 
                'year': year,
                'month': month,
                'by': BY_MAP.get(month_tag.groups()[2], 'month')}

    quarter_tag = QUARTER_TAG.match(col_tag)
    if quarter_tag is not None:
        year = quarter_tag.groups()[0]
        quarter = quarter_tag.groups()[1]
        return {'config_type': 'period',
                'period': 'quarter', 
                'year': year,
                'quarter': quarter,
                'by': BY_MAP.get(quarter_tag.groups()[2], 'quarter')}

    half_tag = HALF_TAG.match(col_tag)
    if half_tag is not None:
        year = half_tag.groups()[0]
        half = half_tag.groups()[1]
        return {'config_type': 'period',
                'period': 'half', 
                'year': year,
                'half': half,
                'by': BY_MAP.get(half_tag.groups()[2], 'half')}

    year_tag = YEAR_TAG.match(col_tag)
    if year_tag is not None:
        year = year_tag.groups()[0]
        return {'config_type': 'period',
                'period': 'year', 
                'year': year,
                'by': BY_MAP.get(year_tag.groups()[1], 'year')}


    ytd_match = YTD_TAG.search(col_tag)
    if ytd_match:
        dt = parse(ytd_match.groups()[1]).date()
        return {'config_type': 'date_range',
                'from': datefuncs.end_of_prev_year(dt.year),
                'to': dt,
                'by': BY_MAP.get(ytd_match.groups()[2], 'year')}

    daily_match = DAILY_TAG.search(col_tag)
    if daily_match:
        dt = parse(daily_match.groups()[1]).date()
        return {'config_type': 'date_range',
                'from': datefuncs.prev_busday(dt),
                'to': dt,
                'by': 'day'}

    trailing12M_match = TRAILING12M_TAG.search(col_tag)
    if trailing12M_match:
        if trailing12M_match.groups()[2]:
            dt = date_from_shortcut(trailing12M_match.groups()[2])
        else:
            dt = datefuncs.today()
        return {'config_type': 'date_range',
                'from': datefuncs.end_of_month(dt.month, dt.year - 1),
                'to': dt,
                'by': 'month'}

    multiyear_match = MULTIYEAR_TAG.search(col_tag)
    if multiyear_match:
        dt = parse(multiyear_match.groups()[1]).date()
        years = int(multiyear_match.groups()[0])
        return {'config_type': 'date_range',
                'from': dt,
                'to': datefuncs.end_of_prev_month(dt.month, dt.year + years),
                'by': BY_MAP.get(multiyear_match.groups()[2], 'year')}

    if col_tag == 'current_YTD':
        return {'config_type': 'period',
                'period': 'year', 
                'year': datefuncs.today().year,
                'by': 'year'}

    if col_tag == 'current_HTD':
        start_of_half = datefuncs.HTD(datefuncs.today())[0]
        half_num = 1 if start_of_half.month == 1 else 2
        return {'config_type': 'period',
                'period': 'half', 
                'year': start_of_half.year,
                'half': half_num,
                'by': 'half'}

    if col_tag == 'current_QTD':
        start_of_qtr = datefuncs.QTD(datefuncs.today())[0]
        qtr_num = 1 + int(start_of_qtr.month - 1) / 3
        return {'config_type': 'period',
                'period': 'quarter', 
                'year': start_of_qtr.year,
                'quarter': qtr_num,
                'by': 'quarter'}

    if col_tag == 'current_MTD':
        today = datefuncs.today()
        return {'config_type': 'period',
                'period': 'month', 
                'year': today.year,
                'month': today.month,
                'by': 'month'}
    # didn't match anything
    raise ValueError('Unexpected shortcut: %s' % repr(col_tag))
