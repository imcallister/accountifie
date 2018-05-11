"""
Used to generate strategy objects for dealing with transactions in query_manager.

To get the default strategy: QueryManagerStrategyFactory().get()
To get a specific strategy:  QueryManagerStrategyFactory().get(strategy='remote')

Also used to compare strategy output. See test/query_manager.py for example.
"""

import difflib
import pandas as pd
import sys
import time
import re

from dateutil.parser import parse as parse_date
from decimal import Decimal
from django.conf import settings
from pandas.util.testing import assert_frame_equal
from .query_manager_remote_strategy import QueryManagerRemoteStrategy
from .query_manager_local_strategy import QueryManagerLocalStrategy
from .query_manager_postgres_strategy import QueryManagerPostgresStrategy
from .query_manager_test_strategy import QueryManagerTestStrategy
from accountifie.common.api import api_func


class QueryManagerStrategyFactory(object):
  def __init__(self):
    self.force_default_strategy = None
    self.strategy_singletons = {
      'remote': QueryManagerRemoteStrategy(),
      'local': QueryManagerLocalStrategy(),
      'test': QueryManagerTestStrategy(),
      'postgres': QueryManagerPostgresStrategy(),
    }
    try:
      self.noop_mutating_functions = api_func('environment', 'variable', 'DISABLE_ACCOUNTIFIE_SVC_MUTATES') == 'true'
    except:
      self.noop_mutating_functions = False

  def override_default_strategy(self, strategy):
    self.force_default_strategy = strategy

  def get(self, strategy=None):
    strategy = strategy or self.__default_strategy()
    if strategy in self.strategy_singletons:
      return self.strategy_singletons[strategy]

    if strategy == 'snapshot':
      return QueryManagerSnapshotStrategy()

    matched_snapshot_strategy = re.match(r'snapshot_(.+)', strategy)
    if matched_snapshot_strategy:
      date_str = matched_snapshot_strategy.group(1)
      snapshot_strategy = QueryManagerSnapshotStrategy()
      date = parse_date(date_str)
      snapshot_strategy.set_cache(date)
      return snapshot_strategy

    raise Exception('Unknown GL strategy: %s. Valid options: [remote, local, snapshot_DATESTRING].' % strategy)

  def get_transaction(self, company_id, transaction_id):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].get_transaction(company_id, transaction_id)

  def upsert_transaction(self, transaction):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].upsert_transaction(transaction)

  def delete_transaction(self, company_id, transaction_id):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].delete_transaction(company_id, transaction_id)

  def delete_bmo_transactions(self, company_id, bmo_id):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].delete_bmo_transactions(company_id, bmo_id)

  def erase(self, company_id):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].erase(company_id)

  def set_fast_inserts(self, company_id, value):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].set_fast_inserts(company_id, value)

  def take_snapshot(self, company_id):
    if not self.noop_mutating_functions:
      for strategy in self.strategy_singletons:
        self.strategy_singletons[strategy].take_snapshot(company_id)

  def compare(self, method_name, method_args):
    fetch_with = lambda obj: getattr(obj, method_name)(**method_args)
    fmt = lambda obj: ', '.join(['%s=%s' % (k, obj[k]) for k in obj])
    column_weights = { 'id': '000', 'date': '001' }
    weigh_column = lambda col: column_weights[col] + col if col in column_weights else '500' + col
    weighted_col_sort = lambda cols: sorted(cols, key=weigh_column)

    remote_start = time.time()
    remote_result = fetch_with(self.get(strategy='remote'))
    remote_time = time.time() - remote_start

    local_start = time.time()
    local_result  = fetch_with(self.get(strategy='local'))
    local_time = time.time() - local_start

    remote_pd = pd.DataFrame(remote_result).fillna(0)
    local_pd =  pd.DataFrame(local_result).fillna(0)

    is_equal = True
    match_error = ''
    try:
      assert_frame_equal(remote_pd, local_pd)
    except:
      match_error = sys.exc_info()[1]
      is_equal = False

    remote_res_str = remote_pd[weighted_col_sort(remote_pd.columns.values)].replace(Decimal(0), Decimal('0.00')).to_csv(sep=',', index=False, header=True).splitlines()
    local_res_str  = local_pd[weighted_col_sort(local_pd.columns.values)].replace(Decimal(0), Decimal('0.00')).to_csv(sep=',', index=False, header=True).splitlines()

    # Header row hack to ensure stays up top
    remote_res_str[0] = '!%s' % remote_res_str[0]
    local_res_str[0] = '!%s' % local_res_str[0]

    remote_res_str.sort()
    local_res_str.sort()

    # diff = difflib.unified_diff(remote_res_str, local_res_str, fromfile='remote_strategy', tofile='local_strategy', n=3)
    diff = difflib.ndiff(remote_res_str, local_res_str)

    print('=== DIFF ===')
    for line in diff:
      print(line)
    print('')

    print('!! Call:    %s(%s)' % (method_name, fmt(method_args)))
    print('!! Matches: %s' % (is_equal))
    if match_error: print('!! Match Error: %s' % match_error)
    print('!! Times:   local %0.2fs, remote %0.2fs' % (local_time, remote_time))
    print('')

  def __default_strategy(self):
    if self.force_default_strategy:
      return self.force_default_strategy

    try:
      return api_func('environment', 'variable', 'DEFAULT_GL_STRATEGY')
    except:
      return settings.DEFAULT_GL_STRATEGY


# in lieu of a cleaner python implementation of singleton pattern
instance = None
def getInstance():
  global instance
  if not instance:
    instance = QueryManagerStrategyFactory()
  return instance
