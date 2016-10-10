
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accountifie.common.table import get_table

@login_required
def tasks_list(request):
    context = {}
    context['title'] = 'Tasks'
    context['content'] = get_table('tasks_list')()
    return render(request, 'tasks_list.html', context)