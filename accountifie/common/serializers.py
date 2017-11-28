
from rest_framework import serializers


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
