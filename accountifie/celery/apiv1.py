import datetime

from djcelery.models import TaskMeta


def _get_info(t):
	data = {}
	data['task_id'] = t['task_id']
	data['date_done'] = t['date_done']
	data['task_status'] = t['result']['status']
	data['result'] = t.get('result', {}).get('result')
	data['task_name'] = t.get('result', {}).get('task_name')
	return data

def tasks_in_progress(qstring={}):
	unfinished = TaskMeta.objects.exclude(status='SUCCESS').values()
	return [_get_info(t) for t in unfinished if t['result']['status']=='IN_PROGRESS']


def tasks_just_finished(qstring={}):
	RECENT = 60 * 60  # 1 hour
	now = datetime.datetime.now()
	cutoff = now - datetime.timedelta(seconds=RECENT)
	data = TaskMeta.objects.filter(date_done__gte=cutoff).values()
	return [_get_info(t) for t in data]
