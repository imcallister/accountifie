
from .celery_main import app as celery_app
from django.http import JsonResponse

import logging

logger = logging.getLogger('default')


def background_task(*args, **kwargs):
    return run_task.delay(*args, **kwargs)


def background_status(request, task_id):
    task = celery_app.AsyncResult(id=task_id)
    rslt = task.result
    rslt.update({'task_id': task_id})
    return JsonResponse(rslt)


@celery_app.task(bind=True)
def run_task(self, *args, **kwargs):
    task_name = kwargs['task']
    self.update_state(state='PROGRESS', meta={'status': 'IN_PROGRESS', 'task_name': task_name})

    try:
        rslts = kwargs['calc'](*args, **kwargs)
        return {'status': 'COMPLETED', 'task_name': task_name, 'output': rslts}
    except Exception as e:
        return {'status': 'FAILED', 'task_name': task_name, 'output': {'error': str(e)}}
    