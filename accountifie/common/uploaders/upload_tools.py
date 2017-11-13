import os
import sys
import traceback
from . import csv

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse

import accountifie.common.uploaders
from accountifie.toolkit.forms import FileForm, LabelledFileForm
from accountifie.toolkit.utils import utcnow, get_default_company

import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def save_file(infile):
    new_name = '%s_%s' % (utcnow().strftime('%Y%m%d%H%M%S'), infile._name)
    if not os.path.exists(INCOMING_ROOT):
        os.makedirs(INCOMING_ROOT)
    full_path = os.path.join(INCOMING_ROOT, new_name)
    with open(full_path, 'wb') as destination:
        for chunk in infile.chunks():
            destination.write(chunk)
    return new_name 


def order_upload(request, processor, redirect_url=None, label=False, file_type='csv upload'):
    if request.method == 'POST':
        
        if label:
            form = LabelledFileForm(request.POST, request.FILES)
        else:
            form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            upload = list(request.FILES.values())[0]
            file_name_with_timestamp = save_file(upload)

            if label:
                summary_msg, error_msgs = processor(file_name_with_timestamp,
                                                    label=form.cleaned_data['label'])
            else:
                summary_msg, error_msgs = processor(file_name_with_timestamp)
            
            messages.success(request, summary_msg)
            for err in error_msgs:
                messages.error(request, err)
        else:
            try:
                upload = list(request.FILES.values())[0]
                file_name_with_timestamp = save_file(upload)
                if label:
                    summary_msg, error_msgs = processor(file_name_with_timestamp,
                                                        label=form.cleaned_data['label'])
                else:
                    summary_msg, error_msgs = processor(file_name_with_timestamp)
                
                return JsonResponse({'summary': summary_msg, 'errors': error_msgs})
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                traceback.print_exc()
                msg = 'Could not process the file provided, please see below'
                return JsonResponse({'summary': msg, 'errors': []})

        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render(request, 'common/upload_csv.html', context)


def csv_to_modelattr(open_file, name_cleaner=None, company=get_default_company()):
    '''takes the fields and values in the CSV and transforms them into a list of dicts where the keys
     will match model attributes. for example Full Description becomes full_description'''
    if name_cleaner == None:
        name_cleaner = lambda name: name
    f_csv = csv.DictReader(open_file) 
    csv_to_modelattr = dict([(name, name_cleaner(name)) for name in f_csv.fieldnames])
    csv_to_modelattr['company_id'] = company

    return [dict([(csv_to_modelattr[name], value) for name, value in list(row.items()) if name in csv_to_modelattr]) for row in f_csv]



def get_foreignkeys(model):
    return dict(((f.name, f.rel.to) for f in model._meta.fields if f.__class__ == models.ForeignKey))

def get_fk_attr(model):
    return [f.name for f in model._meta.fields if f.__class__ == models.ForeignKey]

def get_pk_name(model):
    return model._meta.pk.name
    
def instance_nonrel_data(row, model, name_cleaner=None, value_cleaner=None):
    model_flds =  model._meta.get_all_field_names()
    instance_data_no_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in list(row.items()) if name_cleaner(name)
                        and name_cleaner(name) not in get_fk_attr(model) and name_cleaner(name) in model_flds)
    return model(**instance_data_no_fk)
    
def set_foreignkeys(instance, row, model, name_cleaner=None, value_cleaner=None):
    if get_foreignkeys(model): 
        instance_fk = dict((name_cleaner(name), value_cleaner(name, value)) for name, value in list(row.items()) if name_cleaner(name) 
                        and name_cleaner(name) in get_fk_attr(model))
        for fk in list(get_foreignkeys(model).items()):
            if fk[0] in instance_fk:
                try:
                    related = fk[1].objects.get(pk=instance_fk[fk[0]])
                    setattr(instance, fk[0], related)
                except:
                    logger.error("No ForeignKey %s %s.  %s" % (fk[0], str(fk[1]), instance_fk))
    return instance
    
def dirty_key(row, model=None, unique=None, name_cleaner=None, value_cleaner=None):
    dirty = [name_cleaner(k) for k in list(row.keys()) 
                if name_cleaner(k) not in [f.name for f in [field for field in model._meta.fields 
                        if field not in get_fk_attr(model)]] 
                                if name_cleaner(k)]

    return dirty
    
def create_instance(row, model, name_cleaner=None, value_cleaner=None, unique=None, exclude=[], company=get_default_company()):
    row['company'] = company
    non_rel_instance = instance_nonrel_data(row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)
    if non_rel_instance.id in exclude:
        return None

    full_instance = set_foreignkeys(non_rel_instance, row, model, name_cleaner=name_cleaner, value_cleaner=value_cleaner)    

    return unique(full_instance)
    
