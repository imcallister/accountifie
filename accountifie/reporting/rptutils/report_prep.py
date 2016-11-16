import pkgutil
import inspect
import datetime
from dateutil.parser import parse

from django.shortcuts import render
from django.template import RequestContext

import accountifie.toolkit.utils as utils
from accountifie.reporting.models import ReportDef
from .column_funcs import *
import accountifie.toolkit.utils.datefuncs as datefuncs
import shortcuts


def qs_parse(qs):
    matches = []
    if 'date' in qs:
        matches.append('date')
    
    if 'from' in qs and 'to' in qs:
        matches.append('date_range')

    if 'period' in qs and 'by' in qs:
        matches.append('period')

    if 'col_tag' in qs:
        matches.append('shortcut')

    return matches



def config_fromdate(calc_type, rpt_desc, dt):
    dt = shortcuts.date_from_shortcut(dt)

    if calc_type == 'as_of':
        as_of_col = {dt.strftime('%d-%b-%y'): dt.isoformat()}
    else:
        as_of_col = {str(dt.year): str(dt.year)}
    
    config = {}
    config['columns'] = as_of_col
    config['column_order'] = as_of_col.keys()
    config['title'] = '%s, %s' % (rpt_desc, dt.strftime('%d-%b-%y'))
    config['date'] = dt
    return config


def config_fromperiod(calc_type, rpt_desc, config):
    
    if config['period'] == 'year':
        year_start = datefuncs.start_of_year(config['year'])
        year_end = datefuncs.end_of_year(config['year'])
        if calc_type == 'diff':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_periods(year_start, year_end)
            elif config['by'] == 'quarter':
                columns, column_titles = gen_quarterly_periods(year_start, year_end)
            elif config['by'] == 'half':
                columns, column_titles = gen_semi_periods(year_start, year_end)
            else:
                columns, column_titles = gen_annual_periods(year_start, year_end)
        elif calc_type == 'as_of':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_ends(year_start, year_end)
            elif config['by'] == 'quarter':
                columns, column_titles = gen_quarterly_ends(year_start, year_end)
            elif config['by'] == 'half':
                columns, column_titles = gen_semi_ends(year_start, year_end)
            else:
                columns, column_titles = annual_ends(config['year'])

        title = '%s %s' % (config['year'], rpt_desc)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}

    elif config['period'] == 'semi':
        # could be semi, quarterly, monthly
        half_start = datefuncs.start_of_half(config['half'], config['year'])
        half_end = datefuncs.end_of_half(config['half'], config['year'])

        if calc_type == 'diff':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_periods(half_start, half_end)
            elif config['by'] == 'quarter':
                columns, column_titles = gen_quarterly_periods(half_start, half_end)
            else:
                columns, column_titles = gen_semi_periods(half_start, half_end)
        elif calc_type == 'as_of':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_ends(half_start, half_end)
            elif config['by'] == 'quarter':
                columns, column_titles = gen_quarterly_ends(half_start, half_end)
            else:
                columns, column_titles = gen_semi_ends(half_start, half_end)

        title = '%sH%s %s' % (config['year'], config['half'], rpt_desc)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}
    elif config['period'] == 'quarter':
        # could be quarterly, monthly
        qtr_start = datefuncs.start_of_quarter(config['quarter'], config['year'])
        qtr_end = datefuncs.end_of_quarter(config['quarter'], config['year'])

        if calc_type == 'diff':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_periods(qtr_start, qtr_end)
            else:
                columns, column_titles = gen_quarterly_periods(qtr_start, qtr_end)
        elif calc_type == 'as_of':
            if config['by'] == 'month':
                columns, column_titles = gen_monthly_ends(qtr_start, qtr_end)
            else:
                columns, column_titles = gen_quarterly_ends(qtr_start, qtr_end)

        title = '%sQ%s %s' % (config['year'], config['quarter'], rpt_desc)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}
    elif config['period'] == 'month':
        # could be quarterly, monthly
        mth_start = datefuncs.start_of_month(config['month'], config['year'])
        mth_end = datefuncs.end_of_month(config['month'], config['year'])

        if calc_type == 'diff':
            columns, column_titles = gen_monthly_periods(mth_start, mth_end)
        elif calc_type == 'as_of':
            columns, column_titles = gen_monthly_ends(mth_start, mth_end)
        
        title = '%sM%s %s' % (config['year'], config['month'], rpt_desc)
        return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}


def config_fromdaterange(calc_type, rpt_desc, config):
    from_dt = shortcuts.date_from_shortcut(config['from'])
    to_dt = shortcuts.date_from_shortcut(config['to'])
    if calc_type == 'diff':
        if config['by'] == 'month':
            columns, column_titles = gen_monthly_periods(from_dt, to_dt)
        elif config['by'] == 'quarter':
            columns, column_titles = gen_quarterly_periods(from_dt, to_dt)
        elif config['by'] == 'half':
            columns, column_titles = gen_semi_periods(from_dt, to_dt)
        else:
            columns, column_titles = gen_annual_periods(from_dt, to_dt)
    elif calc_type == 'as_of':
        if config['by'] == 'month':
            columns, column_titles = gen_monthly_ends(from_dt, to_dt)
        elif config['by'] == 'quarter':
            columns, column_titles = gen_quarterly_ends(from_dt, to_dt)
        elif config['by'] == 'half':
            columns, column_titles = gen_semi_ends(from_dt, to_dt)
        else:
            columns, column_titles = gen_annual_ends(from_dt, to_dt)

    title = 'Trailing 12 Months to %s - %s' % (from_dt, rpt_desc)
    return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}


def get_report(rpt_id, company_id, version=None):
    try:
        report = ReportDef.objects.get(name=rpt_id)
        rpt_path = report.path
        rpt_name = report.name
    except:
        return None
    
    loader = pkgutil.get_loader(rpt_path)
    module = loader.load_module(rpt_path)
    
    rpt = None
    for name, obj in inspect.getmembers(module):
        if name == rpt_name:
            rpt = obj(company_id)
            break
    return rpt


def report_prep(request, id):
    qs = dict((k, request.GET.get(k)) for k in request.GET.keys())
    
    if qs.get('company_ID') is None:
        qs['company_ID'] = utils.get_company(request)

    report = get_report(id, qs['company_ID'])
    gl_strategy = request.GET.get('gl_strategy', None)

    if report is None:
        msg = "Report %s does not exist" % id
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False

    if qs['company_ID'] not in report.works_for:
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False

    report.configure(qs)
    report.set_gl_strategy(gl_strategy)

    return report, True


