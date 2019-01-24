from django.contrib import admin

from .models import *


class LogAdmin(admin.ModelAdmin):
    list_display = ('level', 'time', 'message', 'corrId', 'traceback', 'request',)
    
admin.site.register(Log, LogAdmin)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('log', 'status',)
    
admin.site.register(Issue, IssueAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'company',)
    
admin.site.register(Address, AddressAdmin)
