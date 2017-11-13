"""
Strategy that implements basic GL actions for test suite.
See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""

from .query_manager_strategy import QueryManagerStrategy


class QueryManagerTestStrategy(QueryManagerStrategy):

  def create_gl_transactions(self, d2, lines, trans_id, bmo_id):
    pass


  def delete_bmo_transactions(self, company_id, bmo_id):
    pass
