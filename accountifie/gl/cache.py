
"""

Based on Andy Robinson's DoubleTalk accounting framework; used
with permission



Cache for general ledger values

This is a singleton object used for all common 'financial queries' -
balances, activity, history.

The name is misleading.  Long ago I needed an in-memory cache and
spent forever worrying about cache invalidation.  With a well indexed
MySQL database, it turned out to be unnecessary; we just do raw
SQL queries for everything we need.


"""
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
from django.db import connection
from django.conf import settings
from accountifie.common.db import query as qry  #might as well use the standard one
from accountifie.common.api import api_func

DZERO = Decimal('0')

THIS_YEAR_START = date(date.today().year, 1, 1)
THIS_YEAR_END = date(date.today().year + 1, 1, 1) - timedelta(days=1)
INCEPTION = date(2012,12,31)
FOREVER = date(2099,12,31)

# WHAT WE NEED
def get_cache(company_id):
    return GLCache(company_id=company_id)



def normalize_acc(thing):
    if isinstance(thing, str):
        return thing
    elif hasattr(thing, 'id'):  #account
        return thing.id
    else:
        raise ValueError("Expected Account or equivalent text id, but got %s" % repr(thing))

def to_decimal(stuff):
    if stuff is None:
        return DZERO
    else:
        return Decimal(stuff).quantize(DZERO)






class GLCache(object):
    def __init__(self, company_id=None):
        self.company_id = company_id
        self.conn = connection
        self.accts = {}
        self.company_list = api_func('gl', 'company_list', company_id)

    def get_companyID(self):
        return self.company_id

    def query(self, sql, *params):
        return qry(sql, *params)

    ########################################
    # BASIC CHECKS
    def double_entry_check(self):
        "Make sure it adds to zero - return failing transactions"

        sql = """SELECT sum(l.amount)
        FROM gl_tranline l, gl_transaction t
        WHERE t.company_id = ANY(%s)
        AND t.id = l.transaction_id"""
        imbalance = self.query(sql, self.company_list)
        if imbalance:
            #find where

            sql = """SELECT t.id, t.date, t.comment, sum(l.amount)
            FROM gl_transaction t, gl_tranline l
            WHERE t.id = l.transaction_id
            AND t.company_id = ANY(%s)
            GROUP BY t.id
            HAVING sum(l.amount) <> 0
            """
            rows = self.query(sql, self.company_list)
            return rows

    def count(self):
        sql = """SELECT count(t.id) FROM gl_transaction t
              WHERE t.company_id = ANY(%s)"""


        rows = self.query(sql, self.company_list)
        if not rows:
            return 0
        else:
            return rows[0][0]

    def earliest(self):
        sql = "SELECT min(date) from gl_transaction"
        rows = self.query(sql)
        if not rows:
            return date.today()
        else:
            return rows[0][0]

    def latest(self):
        sql = "SELECT max(date) from gl_transaction"
        rows = self.query(sql)
        if not rows:
            return date.today()
        else:
            return rows[0][0]

    def transactions(self):
        # create list of transactions
        # t.comment, t.company_id, t.object_id, t.date
        sql = """SELECT t.id, t.comment, c.name, t.company_id, t.date, t.object_id
        FROM gl_transaction t, django_content_type c
        WHERE t.content_type_id = c.id
        """
        rows = self.query(sql)
        return rows

    def tranlines(self):
        # create list of tranlines
        sql = """SELECT l.id, l.transaction_id, l.amount, a.display_name, a.id, c.name, c.id
        FROM gl_tranline l, gl_account a, gl_counterparty c
        WHERE l.account_id = a.id
        AND c.id = l.counterparty_id
        """
        rows = self.query(sql)
        return rows


    ###################################
    # KILL THIS
    def balance_by_counterparty(self, to_date, account_id):
        "Show the breakdown of the balance. Used for creditors/debtors"
        sql = """
        SELECT l.counterparty_id, sum(l.amount)
        FROM gl_transaction t, gl_tranline l
        WHERE t.id = l.transaction_id
        AND l.account_id = %s
        AND t.date <= %s
        AND t.company_id = ANY(%s)
        GROUP BY l.counterparty_id
        HAVING sum(l.amount) <> 0
        ORDER BY sum(l.amount) DESC
        """
        return self.query(sql, account_id, to_date, self.company_list)

    ########################################
    # NEW STYL GENERIC QUERY

    def get_gl_entries(self, acc_list, from_date=settings.DATE_EARLY, to_date=settings.DATE_LATE):
        sql = """SELECT t.date, t.date_end, t.id, t.comment, l.account_id, l.id, t.company_id, l.counterparty_id, string_agg(c.account_id, ', ') as contra_accounts, string_agg(c.counterparty_id, ', ') as counterparty_ids, l.amount
        FROM gl_tranline l
        INNER JOIN gl_tranline c on c.transaction_id=l.transaction_id
        INNER JOIN gl_transaction t on t.id=l.transaction_id
        WHERE l.account_id = ANY(%s) AND NOT c.account_id = l.account_id
        AND (t.date_end IS NOT NULL OR t.date BETWEEN %s and %s)
        AND (t.date_end IS NULL OR (t.date <= %s AND t.date_end >= %s))
        AND t.company_id = ANY(%s)
        GROUP BY t.id, l.account_id, l.id, t.date, t.comment, l.amount, l.counterparty_id
        ORDER BY t.date;
        """
        rows = self.query(sql,acc_list,from_date, to_date, to_date, from_date, self.company_list)
        if len(rows) == 0:
            return None
        else:
            return pd.DataFrame(rows, columns=['date','date_end','transaction_id','comment','account_id','line_id','company','counterparty','contra_accts','contra_cps','amount']).set_index('line_id')


    def get_gl_entries_trans(self, trans_list, from_date=settings.DATE_EARLY, to_date=settings.DATE_LATE):
        sql = """SELECT t.date, t.date_end, t.id, t.comment, l.account_id, l.id, t.company_id, l.counterparty_id, string_agg(c.account_id, ', ') as contra_accounts, string_agg(c.counterparty_id, ', ') as counterparty_ids, l.amount
        FROM gl_tranline l
        INNER JOIN gl_tranline c on c.transaction_id=l.transaction_id
        INNER JOIN gl_transaction t on t.id=l.transaction_id
        WHERE t.date BETWEEN %s and %s
        AND t.id = ANY(%s)
        GROUP BY t.id, l.account_id, l.id, t.date, t.comment, l.amount, l.counterparty_id
        ORDER BY t.date;
        """
        rows = self.query(sql,from_date, to_date, trans_list)
        if len(rows) == 0:
            return None
        else:
            return pd.DataFrame(rows, columns=['date','date_end','transaction_id','comment','account_id','line_id','company','counterparty','contra_accts','contra_cps','amount']).set_index('line_id')


    def balance(self, acc, date):
        "Balance including entries on given date"
        #whether they passed in a string id or an object, extract the id
        acc = normalize_acc(acc)
        sql = """SELECT sum(l.amount)
        FROM gl_transaction t, gl_tranline l
        WHERE t.id = l.transaction_id
        AND l.account_id = %s
        AND t.date <= %s
        AND t.company_id = ANY(%s)
        """

        rows = self.query(sql, acc, date, self.company_list)

        if not rows:
            return DZERO

        return to_decimal(rows[0][0])




    def get_child_paths(self, path):
        """Return DIRECT child paths.

        Given this, we'd return 'assets.curr.rec'
        even though there is only one rec.clients.  Because I'm lazy
        and it's cleaner for users to understand.
                +---------------------------------+
                | path                            |
                +---------------------------------+
                | assets.curr.ap                  |
                | assets.curr.cashandeq           |
                | assets.curr.fairval.ABSbonds    |
                | assets.curr.fairval.corpbonds   |
                | assets.curr.fairval.equities    |
                | assets.curr.fairval.investments |
                | assets.curr.fairval.loans       |
                | assets.curr.fairval.sovbonds    |
                | assets.curr.other               |
                | assets.curr.rec.clients         |
                | assets.curr.segregated          |
                | assets.curr.stinvest            |
                +---------------------------------+


        """

        from names import DISPLAY_ORDER

        if path.endswith('.'):
            path = path[0:-1]   #we add it ourselves in SQL to remove the current node

        #Can you believe how much escaping we need to get one '%' character through to
        #the database engine?
        sql = "select distinct path, ordering from gl_account where path like '" + path + "%'"
        matches = self.query(sql)


        order_pref = {}
        for (subpath, ordering) in matches:
            order_pref[subpath] = ordering
        order_pref.update(DISPLAY_ORDER)


        nodes = len(path.split("."))
        children = set()
        for row in matches:
            subpath = row[0]
            ordering = row[1]
            parts = subpath.split(".")
            count = len(parts)
            if count == 1 + nodes:
                children.add(subpath)
            elif count >= 1+nodes:
                #e.g. jump from
                #   assets.curr.cashandeq
                #to
                #   assets.curr.cashandeq.checking.jpm
                #without having an actual account for 'checking'
                #then we should infer its existence
                nextbranch = ".".join(parts[0:1+nodes])
                children.add(nextbranch)
        #Take our list of branches and sort in order

        sorter = []
        for subpath in children:
            priority = order_pref.get(subpath, 0)
            sorter.append((priority, subpath))
        sorter.sort()
        return [b for (a,b) in sorter]
