import datetime
import mock
from django.test import TestCase

from accountifie.gl.models import Account, Company, Counterparty
from accountifie.reporting.core_reports.trialbalance import TrialBalance
from accountifie.query.query_manager_strategy import QueryManagerStrategy

class TrialBalanceTestCase(TestCase):
  def setUp(self):
    self.default_company = Company(name='TEST_COMPANY', id='TEST')
    self.default_company.save()

    Account(id='1001', path='test.one', display_name='TestOne', role='asset').save()
    Account(id='1002', path='test.two', display_name='TestTwo', role='expense').save()
    Account(id='1003', path='test.three', display_name='TestThree', role='liability').save()

  def test_trial_balance_happy_path(self):
    # setup mock strategy
    mock_strategy = mock.create_autospec(QueryManagerStrategy, instance=True)
    mock_strategy.account_balances_for_dates.return_value = {
      'balance': {
        '1001': 11.00,
        '1002': 22.00,
        '1003': 33.00
      }
    }

    # create trial_balance
    trial_balance = TrialBalance('TEST')
    trial_balance.set_gl_strategy(mock_strategy)

    # run calc
    result = trial_balance.calcs()

    # test calls
    mock_strategy.account_balances_for_dates.assert_called_once_with(
      company_id='TEST',
      account_ids=['1001', '1002', '1003'],
      # TODO: remove hardcoded start date
      dates={'balance': {'start': datetime.date(2013, 1, 1), 'end': None}},
      with_counterparties=None,
      excl_interco=False,
      excl_contra=None,
      with_tags=None,
      excl_tags=None
    )

    # test result
    self.assertEqual(result[0]['label'], '1001: TestOne')
    self.assertEqual(result[0]['Credits']['text'], 0.0)
    self.assertEqual(result[0]['Debits']['text'], 11.0)

    self.assertEqual(result[1]['label'], '1002: TestTwo')
    self.assertEqual(result[1]['Credits']['text'], 0.0)
    self.assertEqual(result[1]['Debits']['text'], 22.0)

    self.assertEqual(result[2]['label'], '1003: TestThree')
    self.assertEqual(result[2]['Credits']['text'], -33.0)
    self.assertEqual(result[2]['Debits']['text'], 0.0)

    self.assertEqual(result[3]['label'], 'Totals')
    self.assertEqual(result[3]['Credits']['text'], -33.0)
    self.assertEqual(result[3]['Debits']['text'], 33.0)
