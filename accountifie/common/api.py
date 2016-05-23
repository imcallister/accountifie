import json
import logging
import importlib
import sys
import traceback

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


logger = logging.getLogger('default')

def api_wrapper(func):
    def api_call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            ex_type, ex, tb = sys.exc_info()
            logger.info('error in api call: %s.%s --- %s' %(func.__module__, func.__name__, ex))
            return None
    return api_call


def resource_func(group, resource, qstring={}):
    api_module = get_module('%s.%s' % (group, 'apiv1'))
    api_method = getattr(api_module, resource)
    api_call = api_wrapper(api_method)
    return api_call(qstring)


def item_func(group, resource, item, qstring={}):
    api_module = get_module('%s.%s' % (group, 'apiv1'))
    api_method = getattr(api_module, resource)
    api_call = api_wrapper(api_method)
    return api_call(str(item), dict(qstring))


def get_module(group):
    try:
        return importlib.import_module(group)
    except:
        pass

    try:
        return importlib.import_module('accountifie.%s' % group)
    except:
        logger.error("couldn't find api group %s" % group)
        return None

def api_func(*args, **kwargs):
    qs = kwargs.get('qstring', {})
    if len(args)==2:
        return resource_func(args[0], args[1], qstring=qs)
    elif len(args)==3:
        return item_func(args[0], args[1], args[2], qstring=qs)
    else:
        logger.error('error calling api_func: %s' % str(args))


def get_resource(request, group, resource):
    qs = dict((k,v) for k,v in request.GET.iteritems())
    raw = (qs.get('raw') == 'true')
    context = {'data': json.dumps(resource_func(group, resource, qstring=qs), cls=DjangoJSONEncoder, indent=2)}
    context['title'] = 'API call: /%s/%s' % (group, resource)
    if raw:
        return HttpResponse(context['data'], content_type="application/json")
    else:
        return render_to_response('api_display.html', context, context_instance = RequestContext(request))


def get_item(request, group, resource, item):
    qs = request.GET.copy()
    raw = (qs.get('raw') == 'true')
    context = {}
    context['data'] = json.dumps(item_func(group, resource, item, qstring=qs), cls=DjangoJSONEncoder, indent=2)
    context['title'] = 'API call: /%s/%s/%s' % (group, resource, item)
    if raw:
        return HttpResponse(context['data'], content_type="application/json")
    else:
        return render_to_response('api_display.html', context, context_instance = RequestContext(request))
