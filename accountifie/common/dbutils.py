"""
Adapted with permission from ReportLab's DocEngine framework
"""


from django.apps import apps
from django.db import models


def all_concrete_models():
    return [(app, [model for model in apps.get_models(app) if not model._meta.abstract]) for app in apps.get_apps() if apps.get_models(app)]

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