
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class McModel(models.Model):

    class Meta:
        abstract = True


    def to_json(self, expand=[]):
        flds = [f.name for f in self._meta.fields]
        properties = [p for p in getattr(self, 'properties', []) if p in expand]

        data = {}
        for fld in flds:
            if isinstance(self._meta.get_field_by_name(fld)[0], models.ForeignKey) and fld in expand:
                try:
                    data[fld] = getattr(self, fld).to_json(expand=expand)
                except:
                    data[fld] = str(getattr(self, fld))
            else:
                data[fld] = str(getattr(self, fld))

        for prop in properties:
            data[prop] = getattr(self, prop)
        return data


"""
Adapted with permission from ReportLab's DocEngine framework
"""


class Log(models.Model):
    '''Log data for any internal housekeeping'''
    level = models.CharField(max_length = 10)
    time = models.DateTimeField(auto_now_add = True, blank = True)
    message = models.TextField()
    traceback = models.TextField()
    request = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Log entries'
        ordering = ['-time','id']
    
    def __unicode__(self):
            return 'Log("%s", %s, "%s...")' % (self.level, self.time, self.message[0:50])


class TaskMonitor(models.Model): 
    '''Keep track of task id's and the users associated with them'''
    TASK_STATES=(('started', 'started'),('failed', 'failed'), ('succeeded', 'succeeded'))
    task_id = models.CharField(max_length=200, null=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    task_name = models.CharField(max_length=200, null=True)
    percent_complete = models.IntegerField(null=True, default=0)
    task_state = models.CharField(max_length=200, null=True, choices=TASK_STATES)
    traceback = models.TextField(null=True)
    log_info = models.TextField(null=True)
    initiator = models.CharField(max_length=200, null=True)
    
    class Meta:
        ordering = ['-creation_timestamp']
    
    def __unicode__(self):
        return "monitor for %s, %s" % (self.task_name, self.task_id)
