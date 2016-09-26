from django.template import Context
from django.template.loader import get_template


def get_bstrap_table(data_url, row_defs, pagination="true", pagination_num=25):
    context = {}

    if '?' in data_url:
        context['data_url'] = data_url + '&raw=true'
    else:
        context['data_url'] = data_url + '?raw=true'

    context['row_defs'] = row_defs
    context['pagination'] = pagination
    context['pagination_num'] = pagination_num

    tmpl = get_template('bstrap_table.html')
    return tmpl.render(Context(context))


def get_modal(content, modal_title, modal_id):
    context = {}
    context['content'] = content
    context['modal_id'] = modal_id
    context['modal_title'] = modal_title

    tmpl = get_template('modal_cmpnt.html')
    return tmpl.render(Context(context))
