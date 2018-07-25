from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin

from .models import TranLine


class TranLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['counterparty']
    
    counterparty = serializers.CharField(source='counterparty.name')

    class Meta:
        model = TranLine
        fields = ('id', 'date', 'bmo_id', 'counterparty', 'account_id', 'amount', 'comment', 'trans_id')
