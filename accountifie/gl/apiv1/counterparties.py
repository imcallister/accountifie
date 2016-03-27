from accountifie.gl.models import Counterparty

def counterparties(qstring={}):
    data = list(Counterparty.objects.order_by('id').values())
    return data


def counterparty(cp_id, qstring={}):
    cp = Counterparty.objects.filter(id=cp_id).first()
    if cp is None:
        return {}
    else:
        return dict((k,v) for k,v in cp.__dict__.iteritems() if k in ['id','name'])
