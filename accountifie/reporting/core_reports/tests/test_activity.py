import datetime
import mock
from django.test import TestCase

from accountifie.gl.models import Account, Company, Counterparty
from accountifie.reporting.core_reports.activity import AccountActivity
from accountifie.query.query_manager_strategy import QueryManagerStrategy

class ActivityTestCase(TestCase):
  def setUp(self):
    self.default_company = Company(name='TEST_COMPANY', id='TEST')
    self.default_company.save()

    Account(id='1001', path='test.one', display_name='TestOne', role='asset').save()
    Account(id='1002', path='test.two', display_name='TestTwo', role='expense').save()
    Account(id='1003', path='test.three', display_name='TestThree', role='liability').save()

  def test_activity_happy_path(self):
    # setup mock strategy
    mock_strategy = mock.create_autospec(QueryManagerStrategy, instance=True)
    mock_strategy.account_balances_for_dates.return_value = {
      '2014-12-31': {
        '1001': 10.00,
        '1002': 0.00,
        '1003': 24.00
      },
       'chg in year': {
        '1001': 100.00,
        '1002': -1.00,
        '1003': 20.00
       }, 
       '2015-12-31': {
        '1001': 110.00,
        '1002': -1.00,
        '1003': 44.00
      }
    }

    # create activity
    activity = AccountActivity('TEST')
    activity.configure({'col_tag': '2015Annual'})
    activity.set_gl_strategy(mock_strategy)

    # run calc
    result = activity.calcs()

    # test calls
    mock_strategy.account_balances_for_dates.assert_called_once_with(
      company_id='TEST',
      account_ids=['1001', '1002', '1003'],
      # TODO: remove hardcoded start date
      dates={'2014-12-31': {'start': datetime.date(2013, 1, 1), 'end': datetime.date(2014,12,31)},
            'chg in period': {'start': datetime.date(2015, 1, 1), 'end': datetime.date(2015,12,31)},
            '2015-12-31': {'start': datetime.date(2013, 1, 1), 'end': datetime.date(2015,12,31)},
      },
      with_counterparties=None,
      excl_interco=False,
      excl_contra=None,
      with_tags=None,
      excl_tags=None
    )

    # test result
    self.assertEqual(result[0]['label'], '1001: TestOne')
    self.assertEqual(result[0]['2014-12-31']['text'], 10.0)
    self.assertEqual(result[0]['chg in period']['text'], 100.0)
    self.assertEqual(result[0]['2015-12-31']['text'], 110.0)

    self.assertEqual(result[1]['label'], '1002: TestTwo')
    self.assertEqual(result[1]['2014-12-31']['text'], 0.0)
    self.assertEqual(result[1]['chg in period']['text'], -1.0)
    self.assertEqual(result[1]['2015-12-31']['text'], -1.0)

    self.assertEqual(result[2]['label'], '1003: TestThree')
    self.assertEqual(result[2]['2014-12-31']['text'], 24.0)
    self.assertEqual(result[2]['chg in period']['text'], 20.0)
    self.assertEqual(result[2]['2015-12-31']['text'], 44.0)

    