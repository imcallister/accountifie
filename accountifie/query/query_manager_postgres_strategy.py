"""
Strategy that performs transaction querying locally.
The tried and tested way of doing things, though not as performant as
query_manager_remote_strategy.py.
See query_manager_strategy.py for interface docs.
Use query_manager_strategy_factory.py to get an instance of this class.
"""
from django.db.models import Sum

from accountifie.gl.models import TranLine

from .query_manager_strategy import QueryManagerStrategy


class QueryManagerPostgresStrategy(QueryManagerStrategy):

    def cp_balances_for_dates(self, company_id, account_ids, dates):
        bals = {}
        for dt in dates:
            qs = TranLine.objects \
                         .filter(company_id=company_id) \
                         .filter(date__lte=dt)
            if account_ids:
                qs = qs.filter(account_id__in=account_ids)

            rslts = qs.values('counterparty_id') \
                      .annotate(Sum('amount'))
            bals[dt] = dict((l['counterparty_id'], l['amount__sum']) for l in rslts)

        return bals

    def account_balances_for_dates(self, company_id, account_ids, dates, with_counterparties, excl_interco, excl_contra,filter_closing_entries=False):
        bals = {}
        for dt in dates:
            qs = TranLine.objects \
                         .filter(company_id=company_id) \
                         .filter(date__lte=dt)
            if filter_closing_entries:
                qs = qs.exclude(closing_entry=True)
            if account_ids:
                qs = qs.filter(account_id__in=account_ids)
            if with_counterparties:
                qs = qs.filter(counterparty_id__in=with_counterparties)

            rslts = qs.values('account_id') \
                      .annotate(Sum('amount'))
            bals[dt] = dict((l['account_id'], l['amount__sum']) for l in rslts)

        return bals
