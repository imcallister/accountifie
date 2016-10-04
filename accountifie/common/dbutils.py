"""
Adapted with permission from ReportLab's DocEngine framework
"""


from django.apps import apps
from django.db import models
from django.conf import settings


if settings.DJANGO_18:
    from django.db.models.loading import cache
    def all_concrete_models():
        return [(app, [model for model in cache.get_models(app) if not model._meta.abstract]) for app in cache.get_apps() if cache.get_models(app)]
else:
    from django.apps import apps
    def all_concrete_models():
        R = [].append
        M = apps.get_models()
        for app_label, models in apps.all_models.iteritems():
            models = [model for name,model in models.iteritems() if model in M and not model._meta.abstract]
            if models:
                R((app_label,models))
        return R.__self__



def field_is_relational(field):
    relational_fields = [models.ForeignKey, models.ManyToManyField, models.OneToOneField]
    return [rel_field for rel_field in relational_fields if isinstance(field, rel_field)]
    
def relational_fields(model):
    return [field for field in model._meta.fields if field_is_relational(field)]

def all_models_with_relation():
    return [(app, [model for model in models if relational_fields(model)]) for app, models in all_concrete_models()]
    
def all_relations():
    return [(app, [[model, [(field, field.rel.to) for field in relational_fields(model)]] 
                                                    for model in models]) 
                                                        for app, models in all_models_with_relation() if models]