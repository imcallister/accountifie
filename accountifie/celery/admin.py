from django.contrib import admin

from djcelery.models import TaskMeta


class TaskMetaAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'date_done', 'result', 'status')
    readonly_fields = ('result',)    
admin.site.register(TaskMeta, TaskMetaAdmin)

