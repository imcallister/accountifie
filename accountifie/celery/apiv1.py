import datetime

from djcelery.models import TaskMeta

from django.utils.safestring import mark_safe

_STATUS_COLOR_CLASS = dict(zip(('IN_PROGRESS', 'COMPLETED', 'FAILED', 'UNKNOWN') , ('info', 'success', 'danger', 'warning')))

def colorise(status):
    return _STATUS_COLOR_CLASS[status]

  
def status_tag(status):
	return mark_safe('<span class="label label-%s">%s</span>' % (
                colorise(status), status)
    )


def _get_info(t):
	data = {}
	data['task_id'] = t['task_id']
	data['date_done'] = t['date_done']
	data['task_status'] = status_tag(t.get('result', {}).get('status', 'UNKNOWN'))
	data['result'] = t.get('result', {}).get('result')
	data['download'] = t.get('result', {}).get('download')
	data['task_name'] = t.get('result', {}).get('task_name')
	return data

def tasks_in_progress(qstring={}):
	unfinished = TaskMeta.objects.exclude(status='SUCCESS').values()
	return [_get_info(t) for t in unfinished if t['result']['status']=='IN_PROGRESS']


def tasks_just_finished(qstring={}):
	RECENT = 60 * 60 * 24 * 7 # last week
	now = datetime.datetime.now()
	cutoff = now - datetime.timedelta(seconds=RECENT)
	data = TaskMeta.objects.filter(date_done__gte=cutoff) \
						   .order_by('-date_done') \
						   .values()
	return [_get_info(t) for t in data]
