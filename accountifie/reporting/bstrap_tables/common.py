from django.template import Context
from django.template.loader import get_template

from accountifie.toolkit.utils import get_bstrap_table


def daily_activity(dt):
    data_url = "/reporting/reports/AccountActivity/?col_tag=daily_%s&format=json" % dt.isoformat()
    row_defs = [{'data_field': 'label', 'value': 'Account', 'formatter': 'nameFormatter'},
                {'data_field': 'Yesterday', 'value': 'Yesterday', 'formatter': 'drillFormatter'},
                {'data_field': 'Change', 'value': 'Change', 'formatter': 'drillFormatter'},
                {'data_field': 'Today', 'value': 'Today', 'formatter': 'drillFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def tasks_list():
    data_url = "/api/celery/tasks_just_finished"
    row_defs = [{'data_field': 'task_name', 'value': 'Task Name', 'formatter': 'nameFormatter'},
                {'data_field': 'task_status', 'value': 'Status', 'formatter': 'nameFormatter'},
                {'data_field': 'date_done', 'value': 'Started', 'formatter': 'timeFormatter'},
                {'data_field': 'task_id', 'value': 'id', 'formatter': 'nameFormatter'},
                {'data_field': 'return_value', 'value': 'Return Value', 'formatter': 'nameFormatter'},
                {'data_field': 'download', 'value': 'Download', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def metrics(label):
    data_url = "/api/reporting/metric/?label=%s" % label
    row_defs = [{'data_field': 'metric', 'value': 'Metric', 'formatter': 'nameFormatter'},
                {'data_field': 'label', 'value': 'Label', 'formatter': 'nameFormatter'},
                {'data_field': 'date', 'value': 'Date', 'formatter': 'dateFormatter'},
                {'data_field': 'balance', 'value': 'Value', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def balance_trends(dt, acct_list=None, accts_path=None, company_id='EFIE'):
    if acct_list:
        data_url = "/reporting/api/balance_trends/?date=%s&acct_list=%s&company_id=%s" %( dt, '.'.join(acct_list), company_id)
    elif accts_path:
        data_url = "/reporting/api/balance_trends/?date=%s&accts_path=%s&company_id=%s" %( dt, accts_path, company_id)

    row_defs = [{'data_field': 'label', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'M_2', 'value': '2 Months Ago', 'formatter': 'drillFormatter'},
                {'data_field': 'M_1', 'value': '1 Month Ago', 'formatter': 'drillFormatter'},
                {'data_field': 'M_0', 'value': 'This Month', 'formatter': 'drillFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def check_external_bals(dt, company_id='EFIE'):
    data_url = "/api/gl/check_external_bals/?date=%s&company_id=%s" % (dt.isoformat(), company_id)
    row_defs = [{'data_field': 'Account', 'value': 'Account', 'formatter': 'nameFormatter'},
                {'data_field': 'Internal', 'value': 'Internal', 'formatter': 'valueFormatter'},
                {'data_field': 'External', 'value': 'External', 'formatter': 'valueFormatter'},
                {'data_field': 'Diff', 'value': 'Diff', 'formatter': 'valueFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def external_bals_history(dt, company_id='EFIE', acct=''):
    data_url = "/api/gl/external_bals_history/?date=%s&company_id=%s&acct=%s" % (dt.isoformat(), company_id, acct)
    row_defs = [{'data_field': 'Date', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'Internal', 'value': 'Internal', 'formatter': 'valueFormatter'},
                {'data_field': 'External', 'value': 'External', 'formatter': 'valueFormatter'},
                {'data_field': 'Diff', 'value': 'Diff', 'formatter': 'valueFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def snapshots():
    data_url = '/api/snapshot/glsnapshot/'
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'desc_link', 'value': 'Description', 'formatter': 'nameFormatter'},
                {'data_field': 'closing_date', 'value': 'Closing Date', 'formatter': 'nameFormatter'},
                {'data_field': 'snapped_at', 'value': 'Snapped At', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)
