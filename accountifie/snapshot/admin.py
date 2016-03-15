from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from accountifie.snapshot.models import GLSnapshot

class GLSnapshotAdmin(admin.ModelAdmin):
    list_display=('closing_date', 'short_desc', 'snapped_at',)

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse('glsnapshots'))

admin.site.register(GLSnapshot, GLSnapshotAdmin)
