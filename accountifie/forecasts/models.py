import logging
from urlparse import urlparse
import datetime
import pandas as pd

from django.db import models
from django.utils.safestring import mark_safe

import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func
from jsonfield import JSONField

logger = logging.getLogger("default")


def _get_model_call(url):
    purl = urlparse(url)
    path = [x for x in purl.path.split('/') if x!='']
    if path[0] != 'api':
        return 'BAD_PATH_URL', ''

    _qs = purl.query
    if _qs == '':
        qs = {}
    else:
        qs = dict((l[0], l[1]) for l in [el.split('=') \
                  for el in _qs.split('&')])
    return path, qs


def _get_calcs(url):
    path, qs = _get_model_call(url)
    if path == 'BAD_PATH_URL':
        return

    if len(path) == 3:
        return api_func(path[1], path[2], qstring=qs)
    elif len(path) == 4:
        return api_func(path[1], path[2], path[3], qstring=qs)



class Forecast(models.Model):
    label = models.CharField(max_length=50, blank=True)
    company = models.ForeignKey('gl.Company', default=utils.get_default_company)
    start_date = models.DateField()
    hardcode_projections = JSONField(blank=True)
    comment = models.TextField(blank=True)
    model = models.TextField(blank=True)

    class Meta:
        app_label = 'forecasts'
        db_table = 'forecasts_forecast'

    def __str__(self):
        return self.label

    @property
    def id_link(self):
        return mark_safe('<a href="/forecasts/forecast/%s/">%s' %( self.id, self.label))


    def get_projections(self):
        hardcoded_projs = self.hardcode_projections
        calcd_projs = _get_calcs(self.model)
        projs = []
        if hardcoded_projs:
            projs += hardcoded_projs
        if calcd_projs:
            projs += calcd_projs
        return projs

    def get_gl_entries(self):
        proj_df = pd.DataFrame(self.get_projections())

        trans_series = proj_df.groupby(['Debit','Credit','Counterparty']).sum().stack()
        trans_df = pd.DataFrame({'amount': trans_series}).reset_index()
        trans_df['date'] = trans_df['level_3'].map(parse_date)
        trans_df['dateEnd'] = trans_df['date']
        trans_df['id'] = trans_df.index.map(lambda x: 'fcast_1_%s' %x)
        trans_df['comment'] = trans_df.apply(lambda row: '%s.%s.%s.%s' % (row['id'],row['Debit'],row['level_3'],row['Counterparty']),axis=1)

        trans_dict = trans_df.to_dict(orient='records')
        gl_entries = [get_gl_entry(tr) for tr in trans_dict]
        return gl_entries


class ProjectionModel(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    as_of = models.DateTimeField()

    def __str__(self):
        return self.name

FREQ_CHOICES = (('MONTHLY', 'Monthly'),
                ('QUARTERLY', 'Quarterly'),
                ('ANNUAL', 'Annual'),
                ('ONE-OFF', 'One-off')
                )


WINDOW_CHOICES = (('M1', 'Previous Month'),
                  ('M3', 'Rolling 3-month'),
                  ('M12', 'Rolling 12-month'),
                  ('A1', '12 Month Lag')
                  )

SCALING_CHOICES = (('PROP', 'Proportional'),
                   )


class ProjModelv1Param(models.Model):
    proj_model = models.ForeignKey(ProjectionModel)
    label = models.CharField(max_length=20)
    account = models.ForeignKey('gl.Account', related_name='param_account')
    contra = models.ForeignKey('gl.Account', related_name='param_contra')
    counterparty = models.ForeignKey('gl.Counterparty')
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES)
    window = models.CharField(max_length=20, choices=WINDOW_CHOICES)
    metric = models.ForeignKey('reporting.Metric')
    scaling = models.CharField(max_length=20, choices=SCALING_CHOICES)



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

