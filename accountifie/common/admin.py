from django.contrib import admin

from models import *


class LogAdmin(admin.ModelAdmin):
    list_display=('level', 'time', 'message', 'traceback', 'request',)
    
admin.site.register(Log, LogAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display=('label', 'name', 'company',)
    
admin.site.register(Address, AddressAdmin)