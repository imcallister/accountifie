from django.contrib import admin
from .models import Variable, Config, Alias

class VariableAdmin(admin.ModelAdmin):
    ordering = ('key',)
    list_display = ('key', 'value')
    
class ConfigAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name',)

class AliasAdmin(admin.ModelAdmin):
    ordering = ('name', 'context',)
    list_display = ('name', 'display_as', 'context',)
    list_filter = ('context',)

admin.site.register(Variable, VariableAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(Alias, AliasAdmin)
