"""
Interface for swappable strategies used for dealing with transactions in QueryManager

Based on the strategy pattern https://en.wikipedia.org/wiki/Strategy_patter
"""
class QueryManagerStrategy(object):
  def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra, with_tags, excl_tags):
    """
    :param company_id:           the company id
                                 e.g. 'INC'
    :param account_ids:          a list of account ids
                                 e.g. [ '3001', '3010' ]
    :param dates:                dictionary of date ranges
                                 e.g. { '2015': { 'start': '2015-01-01', 'end': '2015-12-31' } }
    :param with_counterparties:  list containing transaction counterparties that should be used to calculate the balance
                                 e.g. [ 'jpmc' ]
    :param excl_interco:         boolean indicating intercompany (e.g. 'INC' transaction with 'LLC' contra) transactions should
                                 be excluded if INC and LLC both subs of same company.
                                 e.g. True
    :param excl_contra:          a list of contra account ids to be excluded
                                 e.g. [ '3001' ]
    :param with_tags             a list of tags for which to find GL entries
                                 e.g. ['yearend']
    :param excl_tags             a list of tags for which to exclude GL entries
                                 e.g. ['yearend']

    :return:                     a dictionary of account balances, indexed by date
                                 e.g. { '2015': { '3001': '1503.23', '3010': '1626.23' } }
    """
    raise Exception('Unimplemented: account_balances_for_dates')

  def transactions(self, company_id, account_ids, from_date, to_date, chunk_frequency, with_counterparties, excl_interco, excl_contra):
    """
    :param company_id:          the company id
                                e.g. 'INC'
    :param account_ids:         a list of account ids
                                e.g. [ '3001', '7020' ]
    :param from_date:           get transactions starting on this date
                                e.g. '2015-01-01'
    :param to_date:             get transactions up to and including this date
                                e.g. '2015-01-31'
    :param chunk_frequency:     when to break spanning transactions (e.g. depreciation)
                                e.g. 'end-of-month'
    :param with_counterparties: list for filtering transaction list by a specific counterparty
                                e.g. [ 'jpmc' ]
    :param excl_interco:        boolean indicating intercompany (e.g. 'INC' transaction with 'LLC' contra) transactions should
                                be excluded if INC and LLC both subs of same company.
    :param excl_contra:         a list of contra account ids to be excluded
                                e.g. [ '3001' ]
    :return:                    a list of transactions
                                e.g. [
                                   { date: Date(2015-01-05), id: '270076', comment: '8661368: Egnyte', account_id: '7020', contra_accts: '3000', counterparty: 'egnyte', amount: 90.00  },
                                   { ... }, ...
                                 ]
    """
    raise Exception('Unimplemented: transactions')

  def upsert_transaction(self, transaction):
    """
    :param transaction:     the transaction object to update/create.
                            e.g. [{
                              'id': 12345,
                              'company': 'INC',
                              'comment': 'TEST TEST TEST',
                              'date': '2015-05-15',
                              'date_end': '2015-05-16',
                              'object_id': 1234,
                              'lines': [
                                { 'account': '1002', 'amount': '-10.00', 'counterparty': '(courier)' },
                                { 'account': '1001', 'amount': '10.00',  'counterparty': '(courier)' }
                              ]
                            }]
    :return: None
    """
    pass

  def delete_transaction(self, company_id, transaction_id):
    """
    :param transaction_id:  a string identifying the transaction to delete
    :return: None
    """
    pass

  def create_gl_transactions(self, d2, lines, trans_id, bmo_id):
    """
    :param
    :return: None
    """
    pass

  def delete_bmo_transactions(self, company_id, bmo_id):
    """
    :param bmo_id:  a string identifying the BMO for which to delete transactions
    :return: None
    """
    pass

  def erase(self, company_id):
    """
    :param company_id:      the company id
                            e.g. 'INC'
    :return: None
    """
    pass

  def set_fast_inserts(self, company_id, value):
    """
    :param company_id:      the company id
                            e.g. 'INC'
    :param value: Boolean
    :return:
    """
    pass

  def take_snapshot(self, company_id):
    """
    :param company_id:      the company id
                            e.g. 'INC'
    :return:
    """
    pass
