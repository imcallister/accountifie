import datetime

from djcelery.models import TaskMeta

from django.utils.safestring import mark_safe

_STATUS_COLOR_CLASS = dict(list(zip(('IN_PROGRESS', 'COMPLETED', 'FAILED', 'UNKNOWN') , ('info', 'success', 'danger', 'warning'))))

def colorise(status):
    return _STATUS_COLOR_CLASS[status]

  
def status_tag(status):
	return mark_safe('<span class="label label-%s">%s</span>' % (
                colorise(status), status)
    )

def download_link(url):
	return mark_safe('<a href="%s">Download results</a>' % url
    )

def _get_info(t):
	rslt = t.get('result', {})
	output = rslt.get('output')

	data = {}
	data['task_id'] = t['task_id']
	data['date_done'] = t['date_done']
	
	if rslt:
		data['task_status'] = rslt.get('status', 'UNKNOWN')
		data['task_name'] = rslt.get('task_name')

		if output:
			data['return_value'] = output.get('return_value')
			download = output.get('download')
			if download:
				data['download'] = download_link(output.get('download'))
			data['error'] = output.get('error')
		
	return data

def tasks_in_progress(qstring={}):
	unfinished = list(TaskMeta.objects.exclude(status='SUCCESS').values())
	return [_get_info(t) for t in unfinished if t['result']['status']=='IN_PROGRESS']


def tasks_just_finished(qstring={}):
	RECENT = 60 * 60 * 24 * 7 # last week
	now = datetime.datetime.now()
	cutoff = now - datetime.timedelta(seconds=RECENT)
	data = list(TaskMeta.objects.filter(date_done__gte=cutoff) \
						   .order_by('-date_done').values())
	return [_get_info(t) for t in data]
