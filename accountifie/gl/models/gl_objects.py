import six
from deepdiff import DeepDiff

#import accountifie.gl.bmo
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers



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

"""
class Transaction(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company')
    date = models.DateField(db_index=True)
    date_end = models.DateField(db_index=True, blank=True, null=True)
    comment = models.CharField(max_length=100)
    long_desc = models.CharField(max_length=200, blank=True, null=True)
    bmo_id = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    source_object = GenericForeignKey()

    class Meta:
        app_label = 'gl'
        db_table = 'gl_transaction'

    def __str__(self):
        return '%s' % self.comment

    def save(self):
        db_tr = Transaction.objects.filter(bmo_id=self.bmo_id).first()
        if db_tr is None:
            super(Transaction, self).save()
        else:
            if len(DeepDiff(self._to_dict(), db_tr._to_dict())) > 0:
                print('CHANGED')
                print(DeepDiff(self, db_tr))
                super(Transaction, self).save()
            else:
                print('not saving it')
        self.update_gl()

    def delete(self):
        tranlines = TranLine.objects.filter(transaction__id=self.id)
        for tl in tranlines:
            tl.delete()
        models.Model.delete(self)

    def get_admin_url(self):
        #https://djangosnippets.org/snippets/1916/
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

    def _to_dict(self):
        return dict((f.attname, getattr(self, f.attname))
                    for f in self._meta.fields if f.attname not in ['id'])

    def _tlines_to_dict(self):
        return dict((tl.id, tl._to_dict()) for tl in self.tranline_set.all())

    def get_changes(self):
        db_tr = Transaction.objects.filter(bmo_id=self.bmo_id).first()
        if db_tr is None:
            return {}
        return DeepDiff(self, db_tr)
"""


class TranLine(models.Model):
    #transaction = models.ForeignKey(Transaction)
    company = models.ForeignKey('gl.Company', blank=True, null=True)
    date = models.DateField(db_index=True)
    date_end = models.DateField(db_index=True, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)
    account = models.ForeignKey(Account, blank=True, null=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    counterparty = models.ForeignKey('gl.Counterparty', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    bmo_id = models.CharField(max_length=100, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    source_object = GenericForeignKey()

    class Meta:
        app_label = 'gl'
        db_table = 'gl_tranline'

    def __str__(self):
        return '%.2f: Account %s' %(self.amount, self.account)

    @property
    def date(self):
        return self.transaction.date

    def _to_dict(self):
        return dict((f.attname, getattr(self, f.attname))
                    for f in self._meta.fields if f.attname not in ['id'])


class ExternalBalance(models.Model):
    "Assertion that account X has balance Y on date Z"
    company = models.ForeignKey('gl.Company')
    account = models.ForeignKey(Account)
    date = models.DateField(db_index=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        app_label = 'gl'
        db_table = 'gl_externalbalance'

class DepreciationPolicy(models.Model):
    cap_account = models.ForeignKey(Account, related_name='deppolicy_acct')
    depreciation_account = models.ForeignKey(Account, related_name='deppolicy_depacct')
    depreciation_period = models.PositiveIntegerField()

    class Meta:
        app_label = 'gl'
        db_table = 'gl_depreciationpolicy'
    