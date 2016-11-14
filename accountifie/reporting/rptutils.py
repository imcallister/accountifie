import pkgutil
import inspect
import datetime
from dateutil.parser import parse

from django.shortcuts import render
from django.template import RequestContext

import accountifie.toolkit.utils as utils
from models import ReportDef


def qs_parser(qs):
    matches = []
    if 'date' in qs:
        matches.append('date')
    
    if 'from' in qs and 'to' in qs and 'by' in qs:
        matches.append('date_range')

    if 'period' in qs and 'by' in qs:
        matches.append('period')

    if 'col_tag' in qs:
        matches.append('shortcut')

    return matches


def date_from_shortcut(scut):
    if scut == 'yesterday':
        return utils.yesterday()
    elif scut == 'today':
        return utils.today()
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


def config_fromdate(calc_type, rpt_desc, dt):
    dt = date_from_shortcut(dt)

    if calc_type == 'as_of':
        as_of_col = {dt.strftime('%d-%b-%y'): dt.isoformat()}
    else:
        as_of_col = {str(dt.year): str(dt.year)}
    
    config = {}
    config['columns'] = as_of_col
    config['column_order'] = as_of_col.keys()
    config['title'] = '%s, %s' % (rpt_desc, dt.strftime('%d-%b-%y'))
    config['date'] = dt.isoformat()
    return config


def config_fromtag(calc_type, rpt_desc, col_tag):
    return utils.config_fromcoltag(col_tag, rpt_desc, calc_type)


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
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False, None

    if qs['company_ID'] not in report.works_for:
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render(request, 'rpt_doesnt_exist.html', {'message': msg}), False

    report.configure(qs)
    report.set_gl_strategy(gl_strategy)

    return report, True


