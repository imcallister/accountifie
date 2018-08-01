"""
Based on Andy Robinson's DoubleTalk accounting framework; used
with permission
"""

from decimal import Decimal
import logging
from deepdiff import DeepDiff

from django.db import transaction
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

import accountifie.query.query_manager_strategy_factory as QMSF
from accountifie.environment.models import Variable
from accountifie.gl.models import TranLine, Company, Account, Counterparty

DZERO = Decimal('0')

logger = logging.getLogger('default')
GL_STRATEGY = 'postgres'

def _model_to_id(x):
    return x if type(x) == str else x.id


def get_gl_strategy():
    dflt_strategy = Variable.objects \
                            .filter(key='DEFAULT_GL_STRATEGY') \
                            .first()
    return dflt_strategy.value if dflt_strategy else GL_STRATEGY


def recalc_all():
    for model in apps.get_models():
        if issubclass(model, BusinessModelObject):
            for bmo in model.objects.all():
                logger.info('Saving all objects for %s' % bmo, extra={'corrId': 'ACCOUNTIFIE.GL'})
                try:
                    bmo.save()
                except Exception as e:
                    msg = 'Recalc Fail. %s. %s' % (bmo.__dict__, e)
                    logger.exception(msg, extra={'corrId': 'ACCOUNTIFIE.GL'})

    # delete any orphan tranlines
    for tl in TranLine.objects.all():
        try:
            bmo_obj = tl.content_type.get_object_for_this_type(id=tl.object_id)
            if bmo_obj is None:
                tl.delete()
        except ObjectDoesNotExist as e:
            tl.delete()


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

    def bmo_id(self):
        return '%s.%s' % (self.short_code, self.id)
    
    def delete_from_gl(self):
        "Find and remove all GL entries which depend on self"
        TranLine.objects \
                .filter(bmo_id=self.bmo_id()) \
                .delete()

    def create_gl_transactions(self, lines):
        self.create_postgres_gl_transactions(lines)
        
    def create_postgres_gl_transactions(self, lines):
        if sum(l['amount'] for l in lines) == DZERO:
            db_tl_set = TranLine.objects.filter(bmo_id=self.bmo_id())
            new_tl_set = [TranLine(**l) for l in lines]

            if db_tl_set.count() == 0:
                save_tranlines(None, new_tl_set)
            else:
                db_lines = [tl._to_dict() for tl in db_tl_set]
                new_lines = [tl._to_dict() for tl in new_tl_set]
                chgs = DeepDiff(db_lines, new_lines)
                if len(chgs) > 0:
                    save_tranlines(db_tl_set, new_tl_set)
        else:
            logger.error('Imbalanced GL entries for %s' % self.bmo_id())

    def update_gl(self):
        "Fix up GL after any kind of change"
        lines = self.get_gl_transactions()
        #self.delete_from_gl()
        self.create_gl_transactions(lines)

    def get_gl_transactions(self):
        # Override this.  Create a list of transactions.
        return []

    def get_company(self):
        return self.company.id


def _postgres_lines():
    pass


@transaction.atomic
def save_tranlines(old_tl_set, new_tl_set):
    if old_tl_set:
        old_tl_set.delete()

    for l in new_tl_set:
        try:
            l.save()
        except Exception as e:
            msg = 'Error saving tranlines. %s. %s' % (e, l.__dict__)
            print(msg)
            #logger.exception(msg, extra={'corrId': 'ACCOUNTIFIE.GL'})

def on_bmo_save(sender, **kwargs):
    """Alternative method - maintain GL through a signal

    Master-detail BMOs can't use a simple save hook, and
    instead need to set a signal to call this'
    """
    sender.update_gl()
