from multipledispatch import dispatch

from accountifie.gl.models import Account
from accountifie.common.api import api_wrapper
import logging

logger = logging.getLogger('default')


from django.conf import settings
import os


def filter_it(x, ex_list):
    for e in ex_list:
        if e in x:
            return False
    return True
    

def path_accounts(path, qstring={}):
    excl = qstring.get('excl', None)
    incl = qstring.get('incl', None)

    if excl:
        acct_list = [a for a in list(Account.objects.filter(path__contains=str(path)).values()) if filter_it(a['path'], excl.split(','))]
    elif incl:
        acct_list = [a for a in list(Account.objects.filter(path__contains=str(path)).values()) if not filter_it(a['path'], incl.split(','))]
    else:
        acct_list = list(Account.objects.filter(path__contains=str(path)).values())

    return acct_list


@dispatch(dict)
def account(qstring):
    return list(Account.objects.order_by('id').values())


@dispatch(str, dict)
def account(acct_id, qstring):
    try:
        acct = (list(Account.objects.filter(pk=acct_id)) + list(Account.objects.filter(path=acct_id)))[0]
        flds = ['display_name', 'role', 'path', 'id']
        return dict((k,v) for k,v in acct.__dict__.items() if k in flds)
    except:
        return None


def child_paths(path, qstring={}):
    path_len = len(path.split('.'))
    all_sub_paths = [x.path for x in Account.objects.filter(path__contains=path) if len(x.path.split('.')) > path_len]
    all_child_paths = ['.'.join(x.split('.')[:(path_len+1)]) for x in all_sub_paths]
    return list(set(all_child_paths))

