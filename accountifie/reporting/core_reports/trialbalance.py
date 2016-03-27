import datetime
import copy
from decimal import Decimal
from dateutil.parser import parse
import logging

from accountifie.reporting.models import Report
from accountifie.toolkit.utils import DZERO
import accountifie.toolkit.utils as utils
import accountifie.gl.apiv1 as gl_api


logger = logging.getLogger('default')

class TrialBalance(Report):
    """Left/Right display of each active account on the given date.

    Shamelessly piggbacking on the Report class without really inheriting
    anything, so that the find_reports function will find it.
    """

    def __init__(self, company_id, date=None):

        self.date = date
        self.description = 'Trial Balance'
        self.title = "Trial Balance"
        self.company_id = company_id
        self.columns = {'Debits':'Debits', 'Credits': 'Credits'}
        self.calc_type = 'as_of'
        self.set_company()
        self.works_for = [cmpny['id'] for cmpny in gl_api.companies()]
        self.column_order = ['Debits', 'Credits']
        self.label_map = None
        self.link_map = lambda x: utils.acct_history_link(x.name)
        
        
    def set_columns(self, columns, column_order=None):
        # columns are fixed... don't mistakenly adjust to dates
        pass

    def configure(self, as_of=None, col_tag=None, path=None):
        if as_of:
            if as_of == 'today':
                self.date = datetime.datetime.now().date()    
            else:
                self.date = parse(as_of).date()
            self.title = 'Trial Balance as of %s' % self.date.strftime('%d-%b-%y')
        elif col_tag:
            config = utils.config_fromcoltag(col_tag, self.description, self.calc_type)
            try:
                self.date = config['columns']['Today']
            except:
                self.date = config['columns'][config['column_order'][-1]]
            self.title = config['title']
        else:
            self.date = datetime.datetime.now().date()    

    def calcs(self):
        bals = self.query_manager.pd_acct_balances(self.company_id, {'balance': self.date})
        
        accts = gl_api.accounts()
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