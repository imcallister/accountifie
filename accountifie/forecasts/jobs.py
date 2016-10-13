import os
import logging
import csv

from django.http import HttpResponseRedirect
from django.conf import settings

from models import Forecast
from accountifie.celery import background_task
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils as rptutils


logger = logging.getLogger('default')

REPORTPACK = ['IncBalanceSheet', 'IncomeStatement', 'Cashflow']

def run_forecast(request):
    # create csv output

    config = {}
    config['fcast_id'] = request.GET['forecast']
    config['col_tag'] = request.GET['col_tag']
    
    task_name = 'forecast_reportpack'

    task_id = background_task(task=task_name,
                              calc=_run_forecast,
                              config=config).id
    return HttpResponseRedirect('/tasks/list/')


def _run_forecast(*args, **kwargs):
    config = kwargs['config']
    col_tag = config['col_tag']
    company_id = config.get('company_id', utils.get_default_company())
    fcast_id = config['fcast_id']

    fcast = Forecast.objects.get(id=fcast_id)
    strategy = QueryManagerStrategyFactory().get('forecast')
    strategy.set_cache(fcast_id=fcast_id, proj_gl_entries=fcast.get_gl_entries())

    file_name = 'forecast_%s_reportpack.csv' %(fcast_id)
    path = os.path.join(settings.DATA_ROOT, settings.DOWNLOAD_PATH, file_name)
    
    if not os.path.isdir(settings.DOWNLOAD_OUT):
        os.makedirs(settings.DOWNLOAD_OUT)

    with open(path, 'wb') as f:
        writer = csv.writer(f)

        for report_id in REPORTPACK:
            writer.writerow([report_id])
            report = rptutils.get_report(report_id, company_id)
            report.configure(col_tag=col_tag)
            report.set_gl_strategy(strategy)
            report_data = report.calcs()

            writer.writerow([''] + report.column_order)
            map_values = lambda x: '' if x == '' else str(x['text'])
            for row in report_data:
                writer.writerow([row['label']] + [map_values(row[col]) for col in [x for x in report.column_order if x in row]])
            
            writer.writerow([])
            writer.writerow([])
            writer.writerow([])

    output_url = os.path.join(settings.DATA_URL, settings.DOWNLOAD_PATH, file_name)
    return {'download': output_url}
