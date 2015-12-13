import json
from ast import literal_eval
from os.path import join as _join

from django.conf import settings
from django.template import Library

register = Library()



@register.filter
def file_path(args):
    _args = literal_eval(args)

    return _join(settings.DATA_URL, settings.PDFOUT_PATH,'forecast_%s_%s.csv' %(_args[0], _args[1]))
