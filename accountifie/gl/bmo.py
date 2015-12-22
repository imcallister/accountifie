"""
Based on Andy Robinson's DoubleTalk accounting framework; used
with permission
"""


import types
import logging

import accountifie.gl.models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import accountifie.query.query_manager_strategy_factory as QMSF


logger = logging.getLogger('default')

class BusinessModelObject(object):
    """Something else which has an effect on the GL.
    
    BMOs will typically create General Ledger entries when
    saved.  They should efficiently update/change their
    GL entries and not create database churn unless there
    is a change.
    
    Make other models inherit from this as a mixin.

    Regrettably one then needs to override save() and
    delete() for the other models, until I find a cunning
    way to make it happen.
    
    """
    
    def delete_from_gl(self):
        "Find and remove all GL entries which depend on self"
        
        my_type = ContentType.objects.get_for_model(self)
        for t in accountifie.gl.models.Transaction.objects.filter(object_id=self.id, content_type=my_type):
            #logger.info('Deleting transaction %s. ID=%s, Company=%s' % (t, t.id, t.company))
            QMSF.QueryManagerStrategyFactory().delete_transaction(t.company.id, t.id)
            t.delete()

    def create_gl_transactions(self, trans):
        "Make any GL transactions this needs"
        for trandict in trans:
            d2 = trandict.copy()
            lines = d2.pop('lines')
            trans_id = d2.pop('trans_id')
            if not d2.has_key('date_end'):
                d2['date_end'] = d2['date']

            tran = accountifie.gl.models.Transaction(**d2)
            tran.source_object = self
            
            try:
                if len(tran.comment) >= 100:
                    tran.comment = tran.comment[:99]
            except:
                pass
            tran.save()
            
            for (account, amount, counterparty) in lines:
                if type(account) in types.StringTypes:
                    account = accountifie.gl.models.Account.objects.get(id=account)
                tran.tranline_set.create(account=account, amount=amount, counterparty=counterparty)

            QMSF.QueryManagerStrategyFactory().upsert_transaction({
                'id': tran.id,
                'bmo_id': trans_id,
                'object_id': tran.object_id,
                'date': str(tran.date),
                'date_end': str(tran.date_end or tran.date),
                'comment': tran.comment,
                'company': tran.company.id if isinstance (tran.company, accountifie.gl.models.Company) else tran.company,
                'type': tran.content_type.name,
                'lines': [{
                    'account': account.id if isinstance (account, accountifie.gl.models.Account) else account,
                    'amount': "{0:.2f}".format(amount),
                    'counterparty': counterparty.id if isinstance (counterparty, accountifie.gl.models.Counterparty) else counterparty,
                    'counterparty': project.id if isinstance (project, accountifie.gl.models.Project) else project
                } for account, amount, counterparty, project in lines]
            })

    def update_gl(self):
        "Fix up GL after any kind of change"
        trans = self.get_gl_transactions()
        self.delete_from_gl()
        self.create_gl_transactions(trans)
        
    
    def get_gl_transactions(self):
        """Override this.  Create a list of transactions.
        
        Create a list of transactions in dictionary form
        which should exist.  It will create them all in the
        GL on saving if they do not already exist.
        """
        return []
        
def on_bmo_save(sender, **kwargs):
    """Alternative method - maintain GL through a signal
    
    Master-detail BMOs can't use a simple save hook, and
    instead need to set a signal to call this'
    """
    sender.update_gl()


