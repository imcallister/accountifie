from .models import Alias, Variable, Config


def alias(name, qstring):
    try:
        alias = Alias.objects.get(name=name)
        return dict((k, getattr(alias, k)) for k in ['display_as', 'name'])
    except:
        return None

def variables(qstring):
    return list(Variable.objects.order_by('id').values())

def variable(key, qstring):
    try:
        return Variable.objects.get(key=key).value
    except:
        raise ValueError("Can't find system variable %s" % key)

def variable_list(key, qstring):
    try:
        return Variable.objects.get(key=key).value.split(',')
    except:
        raise ValueError("Can't find system variable %s" % key)


def config(name, qstring):
    try:
        return Config.objects.get(name=name).reporting
    except:
        raise ValueError("Can't find config variable %s" % key)