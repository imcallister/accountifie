from django.contrib import admin
from accountifie.cal.models import Year, Quarter, Month, Week, Day

class YearAdmin(admin.ModelAdmin):
    fields = ('id',)
admin.site.register(Year, YearAdmin)

class QuarterAdmin(admin.ModelAdmin):
    fields = ('id','year',)
    list_filter = ('id','year',)
admin.site.register(Quarter, QuarterAdmin)

class MonthAdmin(admin.ModelAdmin):
    fields = ('id','quarter','year',)
    list_filter = ('quarter','year',)
admin.site.register(Month, MonthAdmin)

class WeekAdmin(admin.ModelAdmin):
    fields = ('id','first_day','last_day','start_month','end_month','year')
    list_filter = ('first_day','last_day','start_month','end_month','year')    
admin.site.register(Week, WeekAdmin)

class DayAdmin(admin.ModelAdmin):
    fields = ('id','month','quarter','year')
list_filter = ('month','quarter','year')    
admin.site.register(Day, DayAdmin)
