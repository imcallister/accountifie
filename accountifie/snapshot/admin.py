from django.contrib import admin

from accountifie.snapshot.models import GLSnapshot

class GLSnapshotAdmin(admin.ModelAdmin):
    list_display=('closing_date', 'short_desc', 'snapped_at',)

admin.site.register(GLSnapshot, GLSnapshotAdmin)
