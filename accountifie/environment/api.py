from .models import Alias, Variable, Config

def get(api_view, params):
    return globals()[api_view](params)


def alias(params):
    try:
        alias = Alias.objects.get(name=params['name'])
        return dict((k, getattr(alias, k)) for k in ['display_as', 'name'])
    except:
        return None

def variable(params):
    try:
        return Variable.objects.get(key=params['name']).value
    except:
        raise ValueError("Can't find system variable %s" % params['name'])

def variable_list(params):
    try:
        return Variable.objects.get(key=params['name']).value.split(',')
    except:
        raise ValueError("Can't find system variable %s" % params['name'])


def config(params):
    try:
        return Config.objects.get(name=name).reporting
    except:
        raise ValueError("Can't find config variable %s" % params['name'])