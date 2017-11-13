"""
Based on Andy Robinson's DoubleTalk accounting framework; used
with permission
"""

from decimal import Decimal
import types
import logging

import accountifie.gl.models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import accountifie.query.query_manager_strategy_factory as QMSF


DZERO = Decimal('0')

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
        bmo_id = '%s.%s' %(self.short_code, self.id)
        QMSF.getInstance().get().delete_bmo_transactions(self.company.id, bmo_id)


    def create_gl_transactions(self, trans):
        
        "Make any GL transactions this needs"
        for trandict in trans:
            d2 = trandict.copy()
            
            if 'date_end' not in d2:
                d2['date_end'] = d2['date']

            try:
                tags = ','.join(d2.pop('tags'))
            except:
                tags = ''

            d2['company'] = d2['company'].id if isinstance (d2['company'], accountifie.gl.models.Company) else d2['company']

            lines = d2.pop('lines')
            trans_id = d2.pop('trans_id')
            bmo_id = d2.pop('bmo_id')

            lines = [{
                        'account': account.id if isinstance (account, accountifie.gl.models.Account) else account,
                        'amount': "{0:.2f}".format(amount),
                        'counterparty': counterparty.id if isinstance (counterparty, accountifie.gl.models.Counterparty) else counterparty,
                        'tags': tags
                        } for account, amount, counterparty, tags in lines]
            
            QMSF.getInstance().get().create_gl_transactions(d2, lines, trans_id, bmo_id)

            """
            if GL_strategy == 'local':
                tran = accountifie.gl.models.Transaction(**d2)
                tran.source_object = self
                
                try:
                    if len(tran.comment) >= 100:
                        tran.comment = tran.comment[:99]
                except:
                    pass
                tran.save()    
            
                for (account, amount, counterparty, tags) in lines:
                    if type(account) in types.StringTypes:
                        account = accountifie.gl.models.Account.objects.get(id=account)
                    if type(counterparty) in types.StringTypes:
                        counterparty = accountifie.gl.models.Counterparty.objects.get(id=counterparty)
                    tran.tranline_set.create(account=account, amount=amount, counterparty=counterparty, tags=tags)
                
            elif GL_strategy == 'remote':
                # if we have a balanced transation then upsert
                if sum([line[1] for line in lines]) == DZERO:
                    QMSF.QueryManagerStrategyFactory().upsert_transaction({
                        'id': trans_id,
                        'bmo_id': '%s.%s' %(self.short_code, bmo_id),
                        #'object_id': tran.object_id,
                        'date': str(d2['date']),
                        'date_end': str(d2.get('date_end', None) or d2['date']),
                        'comment': d2['comment'],
                        'company': d2['company'].id if isinstance (d2['company'], accountifie.gl.models.Company) else d2['company'],
                        'type': None,
                        'lines': [{
                            'account': account.id if isinstance (account, accountifie.gl.models.Account) else account,
                            'amount': "{0:.2f}".format(amount),
                            'counterparty': counterparty.id if isinstance (counterparty, accountifie.gl.models.Counterparty) else counterparty,
                            'tags': tags
                        } for account, amount, counterparty, tags in lines]
                    })
            """    

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

    def get_company(self):
        return self.company.id
        
def on_bmo_save(sender, **kwargs):
    """Alternative method - maintain GL through a signal
    
    Master-detail BMOs can't use a simple save hook, and
    instead need to set a signal to call this'
    """
    sender.update_gl()


