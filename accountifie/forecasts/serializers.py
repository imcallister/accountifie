
from .models import ProjModelv1Param
from rest_framework import serializers


class ProjModelv1ParamSerializer(serializers.ModelSerializer):
    proj_model = serializers.StringRelatedField()
    account = serializers.StringRelatedField()
    contra = serializers.StringRelatedField()
    counterparty = serializers.StringRelatedField()
    metric = serializers.StringRelatedField()

    class Meta:
        model = ProjModelv1Param
        fields = ('label', 'proj_model', 'account', 'contra',
                  'counterparty', 'frequency', 'window',
                  'metric', 'scaling')
