from django.contrib import admin

from models import *



class ForecastAdmin(admin.ModelAdmin):
    list_display=('id', 'label', 'start_date')


admin.site.register(Forecast, ForecastAdmin)
