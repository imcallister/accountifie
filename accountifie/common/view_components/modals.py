from django.template import Context
from django.template.loader import get_template


def basic_modal(content, modal_title, modal_id):
    context = {}
    context['content'] = content
    context['modal_id'] = modal_id
    context['modal_title'] = modal_title

    tmpl = get_template('modal_cmpnt.html')
    return tmpl.render(Context(context))
