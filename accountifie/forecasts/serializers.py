
from .models import ProjModelv1Param, Forecast
from rest_framework import serializers


class ForecastSerializer(serializers.ModelSerializer):
    #id_link = serializers.Field()

    class Meta:
        model = Forecast
        fields = ('id_link', 'label', 'start_date', 'comment')



class ProjModelv1ParamSerializer(serializers.ModelSerializer):
    proj_model = serializers.StringRelatedField()
    account = serializers.StringRelatedField()
    contra = serializers.StringRelatedField()
    counterparty = serializers.StringRelatedField()
    metric = serializers.StringRelatedField()
    account_id = serializers.SerializerMethodField()
    contra_id = serializers.SerializerMethodField()

    def get_account_id(self, obj):
        return obj.account.id

    def get_contra_id(self, obj):
        return obj.contra.id

    class Meta:
        model = ProjModelv1Param
        fields = ('label', 'proj_model', 'account', 'contra',
                  'counterparty', 'frequency', 'window',
                  'metric', 'scaling', 'account_id', 'contra_id')
