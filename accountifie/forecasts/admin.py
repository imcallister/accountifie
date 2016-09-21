from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import *


class ForecastAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'start_date')

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse('forecasts_index'))

admin.site.register(Forecast, ForecastAdmin)
