
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .apiv1 import tasks_in_progress
from django.http import JsonResponse

@login_required
def tasks_list(request):
    return JsonResponse(tasks_in_progress(), safe=False)
