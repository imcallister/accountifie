from django.contrib import admin
from models import DeferredTask
from django.utils.html import mark_safe, escape

def stdout(obj):
    u = obj.stdout or u''
    return u if not u else mark_safe(u'<pre>%s</pre>' % escape(u))

def stderr(obj):
    u = obj.stderr or u''
    return u if not u else mark_safe(u'<pre>%s</pre>' % escape(u))

class DeferredTaskAdmin(admin.ModelAdmin):
    fields = ('pid', 'start', 'finish', 'runtime', 'task', 'args', 'kwds',
              'finished', 'success', 'hashcode', stdout, stderr, 'progress', 
              'status','username', 'title')
    readonly_fields = fields
    list_display = ('pid', 'task', 'start', 'finish', 'finished', 'success','status','progress', 'username')
    list_filter = ('task', 'finished', 'success', 'username')
    search_fields =('task', 'pid')

    def has_add_permission(self,request,*args,**kwds):
        return False

admin.site.register(DeferredTask, DeferredTaskAdmin)
