from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
def create_report(request):

    if 'date' in request.GET:
        dt = request.GET.get('date')
        rpt = request.GET.get('rpt')
        url = '/reporting/reports/%s?date=%s' % (rpt, dt)
    elif 'mth' in request.GET:
        mth = request.GET.get('mth')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/reporting/reports/%s?col_tag=%sM%s' % (rpt, yr, mth)
    elif 'qtr' in request.GET:
        qtr = request.GET.get('qtr')
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        url = '/reporting/reports/%s?col_tag=%sQ%s' % (rpt, yr, qtr)    
    else:
        rpt = request.GET.get('rpt')
        yr = request.GET.get('yr')
        period = request.GET.get('period')
        url = '/reporting/reports/%s?col_tag=%s%s' % (rpt, yr, period)    

    return HttpResponseRedirect(url)
