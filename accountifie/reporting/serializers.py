
from accountifie.reporting.models import MetricEntry, ReportDef
from rest_framework import serializers


class MetricEntrySerializer(serializers.ModelSerializer):
    metric = serializers.StringRelatedField()

    class Meta:
        model = MetricEntry
        fields = ('metric', 'label', 'date', 'balance')


class ReportDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDef
        fields = ('name', 'description', 'path', 'calc_type')
