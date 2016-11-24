import datetime
import copy
from decimal import Decimal
from dateutil.parser import parse
import logging

from accountifie.reporting.models import Report
from accountifie.toolkit.utils import DZERO
import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func
import accountifie.reporting.rptutils as rptutils


logger = logging.getLogger('default')

class TrialBalance(Report):
    """Left/Right display of each active account on the given date.

    Shamelessly piggbacking on the Report class without really inheriting
    anything, so that the find_reports function will find it.
    """

    def __init__(self, company_id, date=None):
        config = {'description': 'Trial Balance',
                  'calc_type': 'as_of',
                  'date': date}
        
        super(TrialBalance, self).__init__(company_id, **config)

        self.label_map = None
        self.link_map = lambda x: utils.acct_history_link(x.name)
        self.works_for = [cmpny['id'] for cmpny in api_func('gl', 'company')]
        self.columns = {'Debits':'Debits', 'Credits': 'Credits'}
        self.column_order = ['Debits', 'Credits']
        
        
    def set_columns(self, columns, column_order=None):
        # columns are fixed... don't mistakenly adjust to dates
        pass

    def configure(self, config, path=None):
        qs_matches = rptutils.qs_parse(config)
        if len(qs_matches) == 0:
            raise ValueError('Unexpected query string: %s' % repr(config))
        elif len(qs_matches) > 1:
            raise ValueError('Unexpected query string: %s' % repr(config))
        else:
            config['config_type'] = qs_matches[0]


        if config['config_type'] == 'shortcut':
            config.pop('config_type')
            config.update(rptutils.parse_shortcut(config['col_tag']))

        if config['config_type'] == 'date':
            dt = rptutils.date_from_shortcut(config['date'])
            config.update(rptutils.config_fromdate(self.calc_type, self.description, dt))
        elif config['config_type'] == 'date_range':
            dt = rptutils.date_from_shortcut(config['to'])
            config.update(rptutils.config_fromdate(self.calc_type, self.description, dt))
        else:
            raise ValueError('Unexpected query string: %s' % repr(config))
        
        self.set_columns(config['columns'], column_order=config.get('column_order'))
        self.date = config.get('date')
        self.path = config.get('path')
        self.title = 'Trial Balance as of %s' % self.date.strftime('%d-%b-%y')


    def calcs(self):
        bals = self.query_manager.pd_acct_balances(self.company_id, {'balance': self.date})
        
        accts = api_func('gl', 'account')
        accts_map = dict((a['id'], a) for a in accts)

        # dataframe.apply won't work until v0.17 for lambda returning dict... so have to do in roundabout way till then
        debits_map = lambda x: x['balance'] if accts_map[x.name]['role'] in ['asset', 'expense'] else 0
        credits_map = lambda x: -x['balance'] if accts_map[x.name]['role'] in ['liability', 'income', 'capital'] else 0
        
        bals['Debits'] = bals.apply(debits_map, axis=1)
        bals['Credits'] = bals.apply(credits_map, axis=1)
        del bals['balance']

        bals['fmt_tag'] = 'item'
        label_map = lambda x: x + ': ' + accts_map[x]['display_name']
        bals['label'] = bals.index.map(label_map)
        
        totals = bals[self.column_order].sum(axis=0)
        totals['fmt_tag'] = 'major_total'
        totals['label'] = 'Totals'

        bals.loc['Total'] = totals

        bals['index'] = bals.index
        data = bals.to_dict(orient='records')

        credits_link_map = lambda x: utils.acct_history_link(x['index']) if x['index'] != 'Total' and x['Credits'] != '' else ''
        debits_link_map = lambda x: utils.acct_history_link(x['index']) if x['index'] != 'Total' and x['Debits'] != '' else ''
        
        for row in data:
            row['Credits'] = {'text': row['Credits'], 'link':credits_link_map(row)}
            row['Debits'] = {'text': row['Debits'], 'link': debits_link_map(row)}
        
        return data