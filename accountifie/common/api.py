import json
import logging
import importlib
import sys

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse


logger = logging.getLogger('default')

def api_wrapper(func):
    def api_call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            ex_type, ex, tb = sys.exc_info()
            logger.error('error in api call: %s.%s --- %s' %(func.__module__, func.__name__, ex))
            return None
    return api_call


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


def get_resource(request, group, resource):
    api_module = get_module('%s.%s' % (group, 'apiv1'))
    api_method = getattr(api_module, resource)
    qs = request.GET.copy()
    api_call = api_wrapper(api_method)
    return HttpResponse(json.dumps(api_call(qstring=qs), cls=DjangoJSONEncoder), content_type="application/json")


def get_item(request, group, resource, item):
    api_module = get_module('%s.%s' % (group, 'apiv1'))
    api_method = getattr(api_module, resource)
    qs = request.GET.copy()
    api_call = api_wrapper(api_method)
    return HttpResponse(json.dumps(api_call(item, qstring=qs), cls=DjangoJSONEncoder), content_type="application/json")
