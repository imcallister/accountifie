
from rest_framework import serializers

from .models import *


class EagerLoadingMixin:
    """
    Courtesy of
    http://ses4j.github.io/2015/11/23/optimizing-slow-django-rest-framework-performance/
    And see comment from Kyle Bebak for EagerLoadingMixin
    """
    @classmethod
    def setup_eager_loading(cls, queryset):
        if hasattr(cls, "_SELECT_RELATED_FIELDS"):
            queryset = queryset.select_related(*cls._SELECT_RELATED_FIELDS)
        if hasattr(cls, "_PREFETCH_RELATED_FIELDS"):
            queryset = queryset.prefetch_related(*cls._PREFETCH_RELATED_FIELDS)
        return queryset


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('label', 'name', 'company', 'address1',
                  'address2', 'city', 'postal_code', 'province',
                  'country', 'phone', 'email')
