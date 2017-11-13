from django.contrib import admin

from .models import Metric, MetricEntry, ReportDef

class MetricAdmin(admin.ModelAdmin):
    list_display = ('name',)

class MetricEntryAdmin(admin.ModelAdmin):
    list_display = ('metric', 'date', 'balance', 'label', 'as_of')
    list_filter = ('metric', 'label')

class ReportDefAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'path', 'calc_type')


admin.site.register(Metric, MetricAdmin)
admin.site.register(MetricEntry, MetricEntryAdmin)
admin.site.register(ReportDef, ReportDefAdmin)
