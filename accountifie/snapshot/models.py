from django.db import models
from django.utils.safestring import mark_safe

from jsonfield import JSONField

class GLSnapshot(models.Model):
    snapped_at = models.DateTimeField()
    short_desc = models.CharField(max_length=100)
    comment = models.TextField()
    closing_date = models.DateField()




    @property
    def reconciliation(self):
        url = '/snapshot/glsnapshots/balances/%s/?date=%s' % (self.id, self.closing_date.isoformat())

        return mark_safe('<a href="%s">%s' % (url, 'Reconciliation'))


