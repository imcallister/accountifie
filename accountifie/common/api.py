import json
import csv
import itertools
import logging
import importlib
import sys
import traceback
import flatdict

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext


logger = logging.getLogger('default')

def api_wrapper(func):
    def api_call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            ex_type, ex, tb = sys.exc_info()
            logger.exception('error in api call: %s.%s --- %s' %(func.__module__, func.__name__, ex))
            return None
    return api_call


def resource_func(group, resource, qstring={}, chart=False):
    try:
        module_class = 'chart' if chart else 'apiv1'
        api_module = get_module('%s.%s' % (group, module_class))
        api_method = getattr(api_module, resource)
        api_call = api_wrapper(api_method)
        return api_call(qstring)
    except:
        logger.exception('Error calling api %s:%s' % (group, resource))
        return


def item_func(group, resource, item, qstring={}):
    try:
        api_module = get_module('%s.%s' % (group, 'apiv1'))
        api_method = getattr(api_module, resource)
        api_call = api_wrapper(api_method)
        return api_call(str(item), dict(qstring))
    except:
        logger.exception('Error calling api %s:%s:%s' % (group, resource, item))
        return


def get_module(group):
    try:
        return importlib.import_module(group)
    except:
        pass

    try:
        return importlib.import_module('accountifie.%s' % group)
    except:
        logger.exception("couldn't find api group %s" % group)
        return None

def api_func(*args, **kwargs):
    qs = kwargs.get('qstring', {})

    try:
        if len(args)==2:
            return resource_func(args[0], args[1], qstring=qs)
        elif len(args)==3:
            return item_func(args[0], args[1], args[2], qstring=qs)
        else:
            logger.exception('error calling api_func: %s' % str(args))
    except:
        logger.exception('error calling api_func: %s' % str(args))
        return


def get_resource(request, group, resource):
    qs = dict((k, request.GET.get(k)) for k in list(request.GET.keys()))
    raw = (qs.get('raw') == 'true')
    as_csv = (qs.get('as_csv') == 'true')
    if raw:
        return HttpResponse(json.dumps(resource_func(group, resource, qstring=qs), cls=DjangoJSONEncoder), content_type="application/json")
    elif as_csv:
        data = resource_func(group, resource, qstring=qs)
        return output_as_csv(list(data), label=resource)
    else:
        context = {'data': json.dumps(resource_func(group, resource, qstring=qs), cls=DjangoJSONEncoder, indent=2)}
        context['title'] = 'API call: /%s/%s' % (group, resource)
        return render(request, 'api_display.html', context)


def get_chart(request, group, chart):
    qs = dict((k,v) for k,v in request.GET.items())
    return HttpResponse(json.dumps(resource_func(group, chart, qstring=qs, chart=True),
                                   cls=DjangoJSONEncoder), content_type="application/json")


def output_as_csv(data, label='output'):
    if type(data) == list:
        flat_data = [flatdict.FlatDict(d) for d in data]
    else:
        flat_data = [flatdict.FlatDict(data)]

    response = HttpResponse(content_type='text/csv')
    file_name = '%s.csv' % label
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    writer = csv.writer(response)

    cols = list(set(itertools.chain.from_iterable([list(x.as_dict().keys()) for x in flat_data])))
    
    writer.writerow(cols)
    for r in flat_data:
        line = [r.get(c, '') for c in cols]
        writer.writerow(line)
    return response



def get_item(request, group, resource, item):
    qs = dict((k, request.GET.get(k)) for k in list(request.GET.keys()))
    raw = (qs.get('raw') == 'true')
    as_csv = (qs.get('as_csv') == 'true')
    if raw:
        return HttpResponse(json.dumps(item_func(group, resource, item, qstring=qs), cls=DjangoJSONEncoder), content_type="application/json")
    elif as_csv:
        data = item_func(group, resource, item, qstring=qs)
        return output_as_csv(list(data), label='%s:%s' % (resource, item))
    else:
        context = {}
        context['data'] = json.dumps(item_func(group, resource, item, qstring=qs), cls=DjangoJSONEncoder, indent=2)
        context['title'] = 'API call: /%s/%s/%s' % (group, resource, item)
        return render(request, 'api_display.html', context)
