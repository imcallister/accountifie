from __future__ import absolute_import
from .celery import app as celery_app
from django.http import JsonResponse


def background_task(*args, **kwargs):
    return run_task.delay(*args, **kwargs)


def background_status(request, task_id):
    task = celery_app.AsyncResult(id=task_id)
    rslt = task.result
    rslt.update({'task_id': task_id})
    return JsonResponse(rslt)


@celery_app.task(bind=True)
def run_task(self, *args, **kwargs):
    task_name = 'testing' #kwargs['task']
    self.update_state(state='PROGRESS', meta={'status': 'IN_PROGRESS', 'task_name': task_name})
    try:
        rslts = kwargs['calc']()
        return {'status': 'COMPLETED', 'task_name': task_name, 'result': rslts}
    except Exception, e:
        return {'status': 'FAILED', 'task_name': task_name, 'result': {'error': str(e)}}
