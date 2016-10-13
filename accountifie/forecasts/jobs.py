import os
import logging
import csv

from django.http import JsonResponse
from django.conf import settings

from models import Forecast
from accountifie.celery import background_task
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils as rptutils


logger = logging.getLogger('default')


def run_forecast(request):
    # create csv output

    config = {}
    config['fcast_id'] = request.GET['forecast']
    config['report_id'] = request.GET['report']
    config['col_tag'] = request.GET['col_tag']
    
    task_name = 'forecast_%s' % config['report_id']

    task_id = background_task(task=task_name,
                              calc=_run_forecast,
                              config=config).id
    status_url = 'background_task/status/%s' % task_id
    return JsonResponse({'task_id': task_id, 'task_name': task_name, 'status_url': status_url})


def _run_forecast(*args, **kwargs):
    config = kwargs['config']
    report_id = config['report_id']
    col_tag = config['col_tag']
    company_id = config.get('company_id', utils.get_default_company())
    fcast_id = config['fcast_id']

    fcast = Forecast.objects.get(id=fcast_id)
    strategy = QueryManagerStrategyFactory().get('forecast')
    strategy.set_cache(fcast_id=fcast_id, proj_gl_entries=fcast.get_gl_entries())

    report = rptutils.get_report(report_id, company_id)
    report.configure(col_tag=col_tag)
    report.set_gl_strategy(strategy)
    report_data = report.calcs()

    file_name = 'forecast_%s_%s.csv' %(fcast_id, report_id)
    path = os.path.join(settings.DATA_ROOT, settings.DOWNLOAD_PATH, file_name)
    
    if not os.path.isdir(settings.DOWNLOAD_OUT):
        os.makedirs(settings.DOWNLOAD_OUT)

    with open(path, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow([''] + report.column_order)
        map_values = lambda x: '' if x == '' else str(x['text'])
        for row in report_data:
            writer.writerow([row['label']] + [map_values(row[col]) for col in [x for x in report.column_order if x in row]])
    
    output_url = os.path.join(settings.DATA_URL, settings.DOWNLOAD_PATH, file_name)
    return {'download': output_url}
