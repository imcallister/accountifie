import urllib2
import json

from accountifie.common.api import api_func



def lpq():
    base_url = api_func('environment', 'variable', 'ACCOUNTIFIE_SVC_URL')
    url = '%s/lpq/stats' % base_url
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    json_result = json.load(response)
    return json_result


def gl_stats(company_id):
    base_url = api_func('environment', 'variable', 'ACCOUNTIFIE_SVC_URL')
    url = '%s/gl/%s/stats' % (base_url, company_id)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    json_result = json.load(response)
    return json_result
