"""
Based on Andy Robinson's DoubleTalk accounting framework; used
with permission
"""

from decimal import Decimal
import logging

from django.db import transaction

import accountifie.query.query_manager_strategy_factory as QMSF
from accountifie.gl.models import TranLine


DZERO = Decimal('0')

logger = logging.getLogger('default')

GL_STRATEGY = 'local'


def _model_to_id(x):
    return x if type(x) == str else x.id


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
        for td in trans:
            try:
                comment = td['comment'][:99]
            except:
                comment = ''

            # old style
            if GL_STRATEGY == 'local':
                print('=' * 20)
                print(td['lines'][0])
                lines = [{'company_id': _model_to_id(td['company']),
                          'date': td['date'],
                          'date_end': td.get('date_end', td['date']),
                          'comment': comment,
                          'account_id': _model_to_id(account),
                          'amount': Decimal("{0:.2f}".format(amount)),
                          'counterparty_id': _model_to_id(counterparty),
                          'tags': ','.join(tags or []),
                          'bmo_id': td['bmo_id'],
                          'source_object': self
                          } for account, amount, counterparty, tags in td['lines']]
                if sum(l['amount'] for l in lines) == DZERO:
                    # 1. check for balance
                    # 2. check for changes

                    # 3. if any changes then just delete/set to historical
                    #    the prior ones
                    save_tranlines(lines)

                else:
                    logger.error('Imbalanced GL entries for %s' % td['bmo_id'])

            elif GL_STRATEGY == 'remote':
                source_object = {'object_id': self.id,
                                 'model_name': self._meta.model_name,
                                 'app_name': self._meta.app_label}
                td['source_object'] = source_object

                lines = [{'company': _model_to_id(td['company']),
                          'date': str(td['date']),
                          'date_end': str(td.get('date_end', None) or td['date']),
                          'comment': comment,
                          'account': _model_to_id(l['account']),
                          'amount': "{0:.2f}".format(l['amount']),
                          'counterparty': _model_to_id(l['counterparty']),
                          'tags': l.get('tags', None) or [],
                          'bmo_id': td['bmo_id'],
                          'source_object': self
                          } for account, amount, counterparty, tags in td['lines']]
                if sum(l['amount'] for l in lines) == DZERO:
                    QMSF.getInstance() \
                        .get(strategy=GL_STRATEGY) \
                        .create_gl_transactions(td, lines, td['bmo_id'], td['bmo_id'])
                else:
                    logger.error('Imbalanced GL entries for %s' % td['bmo_id'])

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


@transaction.atomic
def save_tranlines(lines):
    for l in lines:
        TranLine(**l).save()


def on_bmo_save(sender, **kwargs):
    """Alternative method - maintain GL through a signal

    Master-detail BMOs can't use a simple save hook, and
    instead need to set a signal to call this'
    """
    sender.update_gl()
