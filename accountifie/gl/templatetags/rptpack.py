import json
from ast import literal_eval
from os.path import join as _join

from django.conf import settings
from django.template import Library

register = Library()


@register.filter
def company(args):
    try:
        _args = json.loads(args)
    except:
        _args = literal_eval(args)


    try:
        return _args[1]
    except:
        return 'unknown'

@register.filter
def file_path(args):
    cpny = company(args)
    return _join(settings.DATA_URL, settings.PDFOUT_PATH,
                   'report_pack_%s.pdf' % cpny)
