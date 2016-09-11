import os
import csv


def csv_to_modelattr(open_file, name_cleaner=None, company=gl_helpers.get_default_company()):
    '''takes the fields and values in the CSV and transforms them into a list of dicts where the keys
     will match model attributes. for example Full Description becomes full_description'''
    if name_cleaner == None:
        name_cleaner = lambda name: name
    f_csv = csv.DictReader(open_file) 
    csv_to_modelattr = dict([(name, name_cleaner(name)) for name in f_csv.fieldnames])
    csv_to_modelattr['company_id'] = company

    return [dict([(csv_to_modelattr[name], value) for name, value in row.items() if name in csv_to_modelattr]) for row in f_csv]



def get_foreignkeys(model):
    return dict(((f.name, f.rel.to) for f in model._meta.fields if f.__class__ == models.ForeignKey))

def get_fk_attr(model):
    return [f.name for f in model._meta.fields if f.__class__ == models.ForeignKey]

def get_pk_name(model):
    return model._meta.pk.name
    
def instance_nonrel_data(row, model, name_cleaner=None, value_cleaner=None):
    model_flds =  model._meta.get_all_field_names()
    instance_data_no_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in row.items() if name_cleaner(name)
                        and name_cleaner(name) not in get_fk_attr(model) and name_cleaner(name) in model_flds)
    return model(**instance_data_no_fk)
    
def set_foreignkeys(instance, row, model, name_cleaner=None, value_cleaner=None):
    if get_foreignkeys(model): 
        instance_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in row.items() if name_cleaner(name) 
                        and name_cleaner(name) in get_fk_attr(model))
        for fk in get_foreignkeys(model).items():
            if instance_fk.has_key(fk[0]):
                try:
                    related = fk[1].objects.get(pk=instance_fk[fk[0]])
                    setattr(instance, fk[0], related)
                except:
                    logger.error("No ForeignKey %s %s.  %s" % (fk[0], str(fk[1]), instance_fk))
    return instance
    
def dirty_key(row, model=None, unique=None, name_cleaner=None, value_cleaner=None):
    dirty = [name_cleaner(k) for k in row.keys() 
                if name_cleaner(k) not in [f.name for f in [field for field in model._meta.fields 
                        if field not in get_fk_attr(model)]] 
                                if name_cleaner(k)]

    return dirty
    
def create_instance(row, model, name_cleaner=None, value_cleaner=None, unique=None, exclude=[], company=gl_helpers.get_default_company()):
    row['company'] = company
    non_rel_instance = instance_nonrel_data(row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)
    if non_rel_instance.id in exclude:
        return None

    full_instance = set_foreignkeys(non_rel_instance, row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)    

    return unique(full_instance)
    
