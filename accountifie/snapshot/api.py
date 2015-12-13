from models import GLSnapshot


def get_record_data(record, flds):
    data = dict((fld, getattr(record, fld)) for fld in flds)
    return data


def get(api_view, params):
    return globals()[api_view](params)

def snapshots(params):
    snaps = GLSnapshot.objects.all().order_by('-snapped_at')
    flds = ['id', 'snapped_at', 'short_desc', 'closing_date', 'reconciliation']
    return [get_record_data(snap, flds) for snap in snaps]
