import logging

import datetime
import pandas as pd

from django.db import models
from django.utils.safestring import mark_safe

from colorful.fields import RGBColorField

from jsonfield import JSONField


logger = logging.getLogger("default")


class Forecast(models.Model):
    label = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    color_code = RGBColorField(blank=True)
    projections = JSONField(blank=True)
    comment = models.TextField()

    class Meta:
        app_label = 'forecasts'
        db_table = 'forecasts_forecast'

    def __str__(self):
        return self.label

    @property
    def id_link(self):
        return mark_safe('<a href="/forecasts/forecast/%s/">%s' %( self.id, self.label))


    def get_gl_entries(self):
        proj_df = pd.DataFrame(self.projections)
        trans_series = proj_df.groupby(['Debit','Credit','Counterparty']).sum().stack()
        trans_df = pd.DataFrame({'amount': trans_series}).reset_index()
        trans_df['date'] =  trans_df['level_3'].map(parse_date)
        trans_df['dateEnd']  = trans_df['date']
        trans_df['id'] = trans_df.index.map(lambda x: 'fcast_1_%s' %x)
        trans_df['comment'] = trans_df.apply(lambda row: '%s.%s.%s.%s' % (row['id'],row['Debit'],row['level_3'],row['Counterparty']),axis=1)

        trans_dict = trans_df.to_dict(orient='records')
        gl_entries = [get_gl_entry(tr) for tr in trans_dict]
        return gl_entries


# utility functions for creating GL entries for Forecast
def parse_date(label):
    lbls = label.split('M')
    yr = int(lbls[0])
    mth = int(lbls[1])
    return datetime.date(yr,mth,1).isoformat()

def get_lines(trans):
    debit = {'accountId': trans['Debit'], 'counterpartyId': trans['Counterparty'], 'amount': trans['amount']}
    credit = {'accountId': trans['Credit'], 'counterpartyId': trans['Counterparty'], 'amount': -trans['amount']}
    return [debit, credit]


def get_gl_entry(trans):
    gl_entry = dict((k, trans[k]) for k in ['id','date','dateEnd','comment'])
    gl_entry['lines'] = get_lines(trans)
    return gl_entry

