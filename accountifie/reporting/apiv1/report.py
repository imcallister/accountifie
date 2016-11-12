
from accountifie.reporting.models import ReportDef
from accountifie.reporting.serializers import ReportDefSerializer


def reportdef(qstring):
    qs = ReportDef.objects.all()
    return ReportDefSerializer(qs, many=True).data

