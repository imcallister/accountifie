import os
from datetime import datetime, timedelta

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import escape

from .utils import utcnow

__all__ = tuple(
    '''DeferredTask setProgress setStatus'''.split()
    )


class DeferredTask(models.Model):
    pid = models.IntegerField(help_text="pid of the process")
    start = models.DateTimeField()
    finish = models.DateTimeField(null=True)
    task = models.CharField(max_length=512,default='')
    args = models.CharField(max_length=512,default='')
    kwds = models.CharField(max_length=512,default='')
    result = models.CharField(max_length=512,null=True)
    finished = models.BooleanField(default=False)
    stdout = models.TextField(default='')
    stderr = models.TextField(default='')
    success = models.BooleanField(default=False)
    hashcode = models.CharField(max_length=32,default='')
    status = models.CharField(max_length=256,default='')
    progress = models.PositiveSmallIntegerField(default='')
    username = models.CharField(max_length=30, default='')
    success_url = models.CharField(max_length=256, blank=True, default='')
    title = models.CharField(max_length=256, blank=True)

    def run_time(self):
        start = self.start
        if start is None:
            return timedelta(seconds=0)
        finish = self.finish
        return (utcnow() if finish is None else finish)- start

    @property
    def runtime(self):
        return str(self.run_time()).split('.')[0]

    def estimated(self):
        if self.finished:
            return self.finish
        if self.progress:
            run_time = self.run_time()
            _seconds = run_time.total_seconds()
            _eta = _seconds * 100/self.progress
            _remaining = timedelta(seconds=int(_eta-_seconds))
            return _remaining
        return None

    def stdout_as_list(self):
        return getattr(self, 'stdout', '').split('\n')

    def stderr_as_list(self):
        return getattr(self, 'stderr', '').split('\n')

    def __str__(self):
        if self.title:
            return u"(%s) %s" % (self.pid, self.title)
        else:
            return u"(%s) %s" % (self.pid, self.finish)

    #needed because somehow it is being referenced before the app is loaded
    class Meta:
        app_label = "tasks"


def setProgress(percent,pid=None):
    """
    percent an integer value between 0-100
    pid optional pid of task to set status for
    """
    if pid is None:
        pid = os.getpid()   #assume we're it
    task = DeferredTask.objects.filter(pid=pid).latest('start')
    task.progress = max(min(int(percent),100),0)
    task.save()


def setStatus(status,pid=None):
    """
    status string stating the phase of the task
    pid optional pid of task to set status for
    """
    if pid is None:
        pid = os.getpid()   #assume we're it
    task = DeferredTask.objects.filter(pid=pid).latest('start')
    task.status = status
    task.save()


def isDetachedTask(pid=None):
    """Check that there is a running Task record with the given or current PID
    """
    if pid is None:
        pid = os.getpid()   #assume we're it
    return DeferredTask.objects.filter(pid=pid, finished=False).exists()
