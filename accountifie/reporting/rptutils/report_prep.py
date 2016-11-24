import pkgutil
import inspect
import datetime
from dateutil.parser import parse

from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext

import accountifie.toolkit.utils as utils
from accountifie.reporting.models import ReportDef
import column_funcs as colfuncs
import accountifie.toolkit.utils.datefuncs as datefuncs
import shortcuts


def qs_parse(qs):
    matches = []
    if 'date' in qs:
        matches.append('date')
    
    if 'from' in qs or 'to' in qs:
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
    period_id = colfuncs.get_period_id(config)

    columns, column_titles = colfuncs.gen_periods(calc_type, config)
    title = '%s %s' % (period_id, rpt_desc)
    return {'title': title, 'columns': dict(zip(column_titles, columns)), 'column_order': column_titles}


def config_fromdaterange(calc_type, rpt_desc, config):
    columns, column_titles = colfuncs.daterange_periods(calc_type, config)
    title = 'From %s to %s. %s' % (config['from'], config['to'], rpt_desc)
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


def history_prep(request):
    config = dict((k, request.GET.get(k)) for k in request.GET.keys())
    
    if config.get('company_id') is None:
        config['company_id'] = utils.get_company(request)

    qs_matches = qs_parse(config)

    if len(qs_matches) == 0:
        config['config_type'] = 'date_range'
        config['from'] = settings.DATE_EARLY
        config['to'] = settings.DATE_LATE
        
    elif len(qs_matches) > 1:
        raise ValueError('Unexpected query string: %s' % repr(config))
    else:
        config['config_type'] = qs_matches[0]

    if config['config_type'] == 'shortcut':
        config.pop('config_type')
        config.update(shortcuts.parse_shortcut(config['col_tag']))

    if config['config_type'] == 'date_range':
        if config.get('from'): 
            config['from'] = shortcuts.date_from_shortcut(config.get('from'))
        if config.get('to'):
            config['to'] = shortcuts.date_from_shortcut(config.get('to'))
    elif config['config_type'] == 'period':
        period_id = colfuncs.get_period_id(config)
        config['from'] = datefuncs.start_of_period(period_id)
        config['to'] = datefuncs.end_of_period(period_id)
        
    return config


def report_prep(request, id):
    
    qs = dict((k, request.GET.get(k)) for k in request.GET.keys())
    if qs.get('company_id') is None:
        qs['company_id'] = utils.get_company(request)

    report = get_report(id, qs['company_id'])
    gl_strategy = request.GET.get('gl_strategy', None)

    if report is None:
        msg = "Report %s does not exist" % id
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False

    if qs['company_id'] not in report.works_for:
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False

    report.configure(qs)
    report.format = qs.get('format', 'html')
    report.set_gl_strategy(gl_strategy)

    return report, True


