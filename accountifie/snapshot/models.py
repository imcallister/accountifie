import pytz

from django.db import models
from django.utils.safestring import mark_safe

from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
from accountifie.common.api import api_func

import logging

logger = logging.getLogger('default')

UTC = pytz.timezone('UTC')

class GLSnapshot(models.Model):
    snapped_at = models.DateTimeField(help_text="Local NY time")
    short_desc = models.CharField(max_length=100)
    comment = models.TextField()
    closing_date = models.DateField()


    def save(self):
        models.Model.save(self)
        logger.info('saving snapshot with snapshot time %s' % self.snapped_at)
        # now create snapshot
        for company_id in [c['id'] for c in api_func('gl', 'company') if c['cmpy_type']=='ALO']:
            fmt = '%Y-%m-%dT%H:%M:%SZ'
            snapshot_time = self.snapped_at.astimezone(UTC).strftime(fmt)
            QueryManagerStrategyFactory().get().take_snapshot(company_id, snapshot_time=snapshot_time)


    @property
    def desc_link(self):
      return mark_safe('<a href="/snapshot/glsnapshots/balances/%s/">%s' %( self.id, self.short_desc))


    @property
    def reconciliation(self):
        url = '/snapshot/glsnapshots/balances/%s/?date=%s' % (self.id, self.closing_date.isoformat())

        return mark_safe('<a href="%s">%s' % (url, 'Reconciliation'))
