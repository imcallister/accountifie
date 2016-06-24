import datetime

from django.template import Library

import accountifie.toolkit.utils as utils

register = Library()


@register.simple_tag
def start_of_year():
    return utils.start_of_year(datetime.datetime.now().year).isoformat()
