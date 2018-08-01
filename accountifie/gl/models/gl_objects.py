import six
from deepdiff import DeepDiff

#import accountifie.gl.bmo
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse



def get_child_paths(path):
    path_len = len(path.split('.'))
    all_sub_paths = [x.path for x in Account.objects.filter(path__contains=path) if len(x.path.split('.')) > path_len]
    all_child_paths = ['.'.join(x.split('.')[:(path_len+1)]) for x in all_sub_paths]
    return list(set(all_child_paths))


class Account(models.Model):
    id = models.CharField(max_length=20, primary_key=True, 
        help_text="Unique short code or number")
    path = models.CharField(max_length=100, db_index=True, unique=True,
        help_text="dotted-path reference to show location on balance sheet")
    ordering = models.IntegerField(default=0)
    display_name = models.CharField(max_length=100, blank=True,
        help_text="the name you would use on a report title")
    role = models.CharField(max_length=10,
        help_text="used in P&L queries and for picklists",
        choices = [
            ('asset', 'asset'),
            ('liability', 'liability'),
            ('income', 'income'),
            ('expense', 'expense'),
            ('capital', 'capital'),
            ]
        )
        
    class Meta:
        ordering = ('id',)
        app_label = 'gl'
        db_table = 'gl_account'
    
    def __str__(self):
        return '%s: %s' % (self.id, self.display_name)


class TranLine(models.Model):
    company = models.ForeignKey('gl.Company', blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    date_end = models.DateField(db_index=True, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    counterparty = models.ForeignKey('gl.Counterparty', blank=True, null=True, max_length=50, on_delete=models.CASCADE)
    bmo_id = models.CharField(max_length=100, blank=True, null=True)
    trans_id = models.CharField(max_length=100, blank=True, null=True)
    closing_entry = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'gl'
        db_table = 'gl_tranline'

    def __str__(self):
        return '%.2f: Account %s' %(self.amount, self.account)

    def _to_dict(self):
        return dict((f.attname, getattr(self, f.attname))
                    for f in self._meta.fields if f.attname not in ['id'])


class ExternalBalance(models.Model):
    "Assertion that account X has balance Y on date Z"
    company = models.ForeignKey('gl.Company', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        app_label = 'gl'
        db_table = 'gl_externalbalance'

class DepreciationPolicy(models.Model):
    cap_account = models.ForeignKey(Account, related_name='deppolicy_acct', on_delete=models.CASCADE)
    depreciation_account = models.ForeignKey(Account, related_name='deppolicy_depacct', on_delete=models.CASCADE)
    depreciation_period = models.PositiveIntegerField()

    class Meta:
        app_label = 'gl'
        db_table = 'gl_depreciationpolicy'
    