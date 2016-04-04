import pkgutil
import inspect

from django.shortcuts import render_to_response
from django.template import RequestContext

import accountifie.toolkit.utils as utils
from models import ReportDef


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
    for name,obj in inspect.getmembers(module):
        if name == rpt_name:
            rpt = obj(company_id)
            break
    
    return rpt


def get_report_cols(path_name, company_ID,as_of=None, col_tag=None):
    rpt = get_report(path_name, company_ID)
    if as_of:
        rpt.config_fromdate(as_of)
    elif col_tag:
        rpt.config_fromtag(col_tag)
    else:
        rpt.config_fromdate('today')

    return rpt.columns, rpt.column_order


def report_prep(request, id):
    as_of = request.GET.get('date', None)
    col_tag = request.GET.get('col_tag', None)

    format = request.GET.get('format', 'html')
    company_ID = request.GET.get('company', utils.get_company(request))
    path = request.GET.get('path', None)
    report = get_report(id, company_ID)
    gl_strategy = request.GET.get('gl_strategy', None)

    if report is None:
        msg = "Report %s does not exist" % id
        return render_to_response('rpt_doesnt_exist.html', RequestContext(request, {'message': msg})), False, None

    if company_ID not in report.works_for:
        msg = "This ain't it. Report not available for %s" % report.company_name
        return render_to_response('rpt_doesnt_exist.html', RequestContext(request, {'message': msg})), False

    report.configure(as_of=as_of, col_tag=col_tag, path=path)
    report.set_gl_strategy(gl_strategy)
    return report, True, format


