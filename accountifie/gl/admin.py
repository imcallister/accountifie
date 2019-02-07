from django.contrib import admin

from .models import *

class TranLineInline(admin.TabularInline):
    model = TranLine

"""
class TransactionAdmin(admin.ModelAdmin):
    list_display=('company', 'id', 'date', 'date_end', 'comment', 'bmo_id', 'source_object')
    list_filter = ('company',)
    ordering = ('-date','id')
    search_fields = ('comment','id',)
    inlines = [
        TranLineInline,
        ]
"""

class TranLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'bmo_id', 'account', 'date', 'amount', 'counterparty',)
    search_fields = ('account__id', 'counterparty__name','id',)
    list_filter = ('account','counterparty')
    search_fields = ('counterparty__name',)
    ordering = ('id',)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'path', 'ordering', 'role')
    list_filter = ('role',)
    search_fields = ('id', 'display_name', 'path')
    ordering = ('id',)
    save_on_top = True
    save_as = True

class ExternalBalanceAdmin(admin.ModelAdmin):
    list_display= ('company','id','account','date','balance','comment')
    ordering = ('-date','account')
    list_filter = ('company','account',)

class DepreciationPolicyAdmin(admin.ModelAdmin):
    list_display =  ('cap_account', 'depreciation_account', 'depreciation_period',)


class DepartmentAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name')
    

class CompanyAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'label', 'name', 'cmpy_type')
    
 
class CounterpartyAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'label', 'name',)
    search_fields = ['id', 'label', 'name']
    
class ProjectAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name',)

class EmployeeAdmin(admin.ModelAdmin):
   
    ordering = ('employee_id',)
    list_display = ('employee_id', 'employee_name', 'e_mail', 'department')
    list_filter = ('department',)

class ExternalAccountAdmin(admin.ModelAdmin):
   
    ordering = ('gl_account',)
    list_display = ('gl_account', 'counterparty', 'name', 'label')
    list_filter = ('gl_account','counterparty',)
    search_fields = ('gl_account',)

admin.site.register(Account, AccountAdmin)
#admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TranLine, TranLineAdmin)
admin.site.register(ExternalBalance, ExternalBalanceAdmin)
admin.site.register(DepreciationPolicy, DepreciationPolicyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Counterparty, CounterpartyAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(ExternalAccount, ExternalAccountAdmin)