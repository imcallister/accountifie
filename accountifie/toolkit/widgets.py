from accountifie.middleware.docengine import getCurrentRequest
import django.template
from django.shortcuts import render

def dropdown_button(current, status, id, others, action):
    t = django.template.loader.get_template('dropdownbutton.html')
    context = django.template.RequestContext(getCurrentRequest())
    context['current'] = current
    context['status'] = status
    context['id'] = id
    context['others'] = dict((x[1],x[0]) for x in others)
    context['action'] = action
    return django.template.loader.render_to_string('dropdownbutton.html',  context)

