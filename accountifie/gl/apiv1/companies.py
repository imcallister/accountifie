from multipledispatch import dispatch

from accountifie.gl.models import Company


@dispatch(str, dict)
def company(company_id, qstring):
    company = Company.objects.get(id=company_id)
    flds = ['cmpy_type', 'color_code', 'name', 'id']
    data = dict((str(k),str(v)) for k,v in company.__dict__.items() if k in flds)

    if company.cmpy_type == 'CON':
        data['subs'] = [sub.id for sub in company.subs.all()]

    return data

@dispatch(dict)
def company(qstring):
    company_list = list(Company.objects.all())
    flds = ['cmpy_type', 'color_code', 'name', 'id']

    data = []

    for company in company_list:
        company_data = dict((str(k),str(v)) for k,v in company.__dict__.items() if k in flds)

        if company.cmpy_type == 'CON':
            company_data['subs'] = [sub.id for sub in company.subs.all()]

        data.append(company_data)

    return data

"""
def companies(qstring={}):
    company_list = list(Company.objects.all())
    flds = ['cmpy_type', 'color_code', 'name', 'id']

    data = []

    for company in company_list:
        company_data = dict((str(k),str(v)) for k,v in company.__dict__.iteritems() if k in flds)

        if company.cmpy_type == 'CON':
            company_data['subs'] = [sub.id for sub in company.subs.all()]

        data.append(company_data)

    return data
"""


def company_list(company_id, qstring={}):
    company = Company.objects.get(id=company_id)
    if company.cmpy_type == 'CON':
        return [sub.id for sub in company.subs.all()]
    else:
        return [company_id]