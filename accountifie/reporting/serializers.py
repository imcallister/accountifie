
from accountifie.reporting.models import MetricEntry
from rest_framework import serializers


class MetricEntrySerializer(serializers.ModelSerializer):
    metric = serializers.StringRelatedField()

    class Meta:
        model = MetricEntry
        fields = ('metric', 'label', 'date', 'balance')
