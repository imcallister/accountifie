import datetime
import pandas as pd
from dateutil.parser import parse


from accountifie.reporting.models import Report
import accountifie.gl.models as gl
import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func


class AccountActivity(Report):

    def __init__(self, company_id, date=None):
        config = {'description': 'Account Activity',
                  'calc_type': 'as_of',
                  'date': date}

        super(AccountActivity, self).__init__(company_id, **config)

        self.label_map = None
        self.link_map = lambda x: utils.acct_history_link(x.name)
        self.works_for = [cmpny['id'] for cmpny in api_func('gl', 'company')]
        self.acct_list = None
        self.equity_sign = False




    def calcs(self):
        if self.path:
            bals = self.query_manager.pd_acct_balances(self.company_id,self.columns, paths=[self.path]).fillna(0.0)
        elif self.acct_list:
            bals = self.query_manager.pd_acct_balances(self.company_id,self.columns, acct_list=self.acct_list, excl_contra=['4150']).fillna(0.0)
        else:
            bals = self.query_manager.pd_acct_balances(self.company_id,self.columns).fillna(0.0)


        if self.equity_sign:
            bals = bals * (-1.0)

        bals.loc['Total'] = bals.apply(sum, axis=0)
        accts = gl.Account.objects.all()
        acct_map = dict((a.id, a.display_name) for a in accts)
        label_map = lambda x: x + ': ' + acct_map[x] if x in acct_map else x
        link_map = lambda x: utils.acct_history_link(x['index']) if x['index'] != 'Total' else ''

        bals['fmt_tag'] = 'item'
        bals['label'] = bals.index.map(label_map)
        bals['index'] = bals.index

        if 'Change' in bals.columns:
            is_small = lambda row: (abs(row['Change']) < 0.5 and row['index'] != 'Total')
            bals = bals[~bals.apply(is_small, axis=1)]

        bals.loc['Total', 'fmt_tag'] = 'major_total'

        data = bals.to_dict(orient='records')

        for row in data:
            for col in self.column_order:
                row[col] = {'text': row[col], 'link': link_map(row)}

        return data
