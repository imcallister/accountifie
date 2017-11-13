# -*- coding:utf-8 -*-

"""
Adapted with permission from ReportLab's DocEngine framework
"""


import json, logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.utils import flatatt, ErrorList
from django.utils.encoding import force_text
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

logger = logging.getLogger('default')

class FileForm(forms.Form):
    file = forms.FileField(required=True)

class LabelledFileForm(forms.Form):
    file = forms.FileField(required=True)
    label = forms.CharField()


class TextCharInput(forms.widgets.TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = 'Click to edit'
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        return format_html('<span{0}>{1}</span>', flatatt(final_attrs), force_text(self._format_value(value)))


# https://djangosnippets.org/snippets/2631/
def add_control_label(f):
    'add class to label_tag'
    def control_label_tag(self, contents=None, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'control-label'
        return f(self, contents, attrs)
    return control_label_tag


class BSErrorList(ErrorList):

    def as_div(self):
        if not self: return ''
        return format_html('<div class="alert {0}">{1}</div>',
                    settings.MESSAGE_TAGS[messages.ERROR],
                    format_html_join('', '<p>{0}</p>',
                        ((force_text(e),) for e in self)
                    )
          )


class ReadOnlyMixin(object):

    class NewMeta:
        readonly = tuple()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyMixin, self).__init__(*args, **kwargs)
        readonly = self.NewMeta.readonly
        if not readonly:
            return
        for name, field in list(self.fields.items()):
            if name in readonly:
                field.widget = SpanWidget(attrs=getattr(field.widget, 'attrs', {}))
            elif not isinstance(field, SpanField):
                continue
            field.widget.original_value = str(getattr(self.instance, name))


class Html5Mixin(object):
    '''
    Implements HTML5 widgets
    Currently focused on date field
    '''
    class Media:
        js = (
            staticfiles_storage.url("common/js/html5form.js"),
            )

    def __init__(self, *args, **kwargs):
        super(Html5Mixin, self).__init__(*args, **kwargs)
        self.Media.js += (staticfiles_storage.url("common/js/html5form.js"),)
        for name, fld in list(self.fields.items()):
            _x = fld.widget.__class__.__name__
            if _x in ('DateInput', 'TimeInput'):
                _x = _x.replace('Input','')
                fld.widget.input_type = _x.lower()
            elif _x == 'DateTimeInput':
                fld.widget.input_type = 'datetime-local'
            if _x=='Date':
                fld.widget.format="%Y-%m-%d"


class Html5Form(Html5Mixin, forms.Form):
    pass


class Html5ModelForm(Html5Mixin, forms.ModelForm):
    pass


class BootstrapMixin(object):
    """
    Inherit with forms.Form or forms.ModelForm
    For example:
        class AnyForm(forms.Form, BootstrapForm):
            pass

        class AnyModelForm(forms.ModelForm, BootstrapForm):
            pass
    """
    bs_horizontal = True
    error_class = BSErrorList


    def render_errors(self):
        if not self.errors:
            return ""
        output = []
        output.append('<div class="alert alert-danger error">')
        output.append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>')
        output.append('<p><strong>%s</strong></p><ul>' % 'There are errors while submitting the form:')
        for field, error in list(self.errors.items()):
            output.append('<li><strong>%s</strong> %s</li>' % (field.title(), error[0]))
        output.append('</ul></div>')
        return mark_safe('\n'.join(output))

    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        self.error_class = BSErrorList
        for name, fld in list(self.fields.items()):
            if not fld.show_hidden_initial:
                if fld.widget.__class__.__name__ == "RadioSelect":
                    #FIXME: we might be missing other custom attributes enforced upstream
                    fld.widget = BootstrapRadioSelect(choices=fld.choices, inline=False)
                else:
                    _class = fld.widget.attrs.get('class','')
                    if len(_class)>0:
                        _class+=' '
                    if fld.widget.__class__.__name__ in \
                            ('NullBooleanSelect', 'BooleanSelect', 'CheckboxInput'):
                        _class.replace('form-control','')
                    else:
                        if 'form-control' not in _class:
                            _class+='form-control'
                    fld.widget.attrs.update({'class':_class,})

    def _render_field(self, obj, level=0, siblings=0):
        if getattr(obj, 'is_fieldset', False):
            output = '<fieldset'
            if getattr(obj, 'css_classes', False):
                output+=' class="%s"' % obj.css_classes
            output += '>'
            for flds in obj:
                kw = {'level': level+1,}
                if getattr(flds, 'is_fieldset', False):
                    kw['siblings'] = len(flds.fieldset.fields)
                else:
                    kw['siblings'] = siblings
                output+=self._render_field(flds,**kw)
            output+='</fieldset>'
            return output
        else:
            if getattr(obj, 'is_hidden', False):
                return  obj.as_widget()

            _div_class = "form-group "
            _label_attrs = {'class': 'control-label',}
            _field_html = '%s'
            _help_tag = '<div class="form-control-static help_block text-muted">%s</div>'

            horizontal_set = (siblings > 1) and (level > 0)

            if horizontal_set:
                _div_class += " col-sm-%d" % (12 // siblings) # bootstrap grid
            else:
                if getattr(obj, 'help_text', False):
                    _field_col_width = 7
                else:
                    _field_col_width = 10
                _div_class += "row"
                #if obj.field.__class__.__name__ == 'GridFormField':
                #    _label_attrs['style']='float:none'
                _label_attrs['class']+= ' col-sm-2'
                _field_html = '<div class="col-sm-%d">' % _field_col_width + '%s</div>'
                _help_tag = '<div class="col-sm-3 form-control-static help_block text-muted">%s</div>'

            row_template = '''
<div class="%(div_class)s">
    %(label)s
    %(field)s
    %(help_text)s
    %(errors)s
</div>
'''
            # check if it is an actual field and not a fieldset from betterforms
            widget_attrs = obj.field.widget.attrs
            widget_classes = widget_attrs.get('class','').split()
            if 'form-control' not in widget_classes and \
                    obj.field.widget.__class__.__name__ not in \
                    ('NullBooleanSelect', 'BooleanSelect',
                     'CheckboxInput','RadioSelect','BootstrapRadioSelect'):
               widget_attrs.update({'class': '%s form-control' % ' '.join(widget_classes)})
            if not obj.field.required:
                _label_attrs['class'] += " text-muted"

            row_dict = {
                "div_class" : _div_class,
                "field" :  _field_html % obj.as_widget(),
                "label" : obj.label_tag(attrs=_label_attrs),
                "help_text" : _help_tag % obj.help_text or '',
                "errors": obj.errors,
            }
            if obj.errors:
                row_dict['help_text']='';
                row_dict["div_class"] = "row form-group alert alert-danger"
                #obj.field.widget.attrs["class"]="error"

            return row_template % row_dict

    def as_div(self):
        'This wont be used by betterforms'
        # FIXME: not integrating with betterforms
        #if BETTERFORMS_LOADED and isinstance(self, BetterForm):
        #    return self
        output = []
        if self.bs_horizontal:
            self._field_html = '<div class="col-sm-%d">%s</div>'
            self._label_attrs = {'class':'col-sm-2 control-label',}
            self._help_tag = '<div class="col-sm-3 help_block">%s</div>'
        else:
            self._field_html = '<!--%s-->%s'
            self._label_attrs = {}
            self._help_tag = '<div class="help_block">%s</div>'

        for flds in self: #see original Form class __iter__ method
            output.append(self._render_field(flds))

        return mark_safe('\n'.join(output))


class BootstrapForm(forms.Form, BootstrapMixin):
    pass


class BootstrapModelForm(forms.ModelForm):

    def as_div(self):
        "Returns this form rendered as Bootstrap HTML"
        return forms.BaseModelForm._html_output(self,
            normal_row = '''<div class="form-group">%(errors)s%(label_tag)s
%(field)s''',
            error_row = '<li>%s</li>',
            row_ender = '</div>',
            help_text_html = ' <div class="help_block">%s</div>',
            errors_on_separate_row = False)



class JEditableMixin(object):

    form_instance_id = None
    form_object_name = None

    class Media:
        js = (
            staticfiles_storage.url("common/js/ajax_setup.js"),
            staticfiles_storage.url("common/js/jquery.jeditable.js"),
            staticfiles_storage.url("common/js/editable.js"),
            staticfiles_storage.url("common/js/jquery.autosize-min.js"),
            )
        if getattr(settings, 'TRACK_AJAX_CALLS', False):
            js+=('common/js/jquery.ajaxtrack.js',)
        css = {
            'screen': ( staticfiles_storage.url("common/css/editable.css"),
                ),
            }

    def as_div(self):
        "Returns this form rendered as HTML <dt /><dd />s -- excluding the <dl></dl>."
        return forms.BaseModelForm._html_output(self,
            normal_row = '%(errors)s<dt>%(label)s</dt><dd%(html_class_attr)s>%(field)s</dd>%(help_text)s',
            error_row = '<li>%s</li>',
            row_ender = '</dd>',
            help_text_html = ' <span class="helptext">%s</span>',
            errors_on_separate_row = False)

    def generate_jeditable_attrs(self, fieldname):
        _instance = self.instance
        _bf, containingmodel, direct, m2m = _instance._meta.get_field_by_name(fieldname)
        _uce = getattr(self.instance, 'user_can_edit', False)
        attrs = {
            #'field_name': _bf.attname,
            # anyone will be able to edit for now
            'data-can_edit': str(_uce(attr=fieldname)) if _uce else "True",
            'data-instance_name': self.__class__.__name__.lower(),
            'data-instance_id': self.instance.pk,
            'data-field_name': _bf.name,
            }
        if getattr(_bf, 'max_length', False):
            attrs.update({'maxlength': getattr(_bf, 'max_length')})
        _klss = ''
        if _bf.choices:
            _klss= 'choice '
            #attrs['choices'] = json.dumps(dict(getattr(_bf, 'choices', {})))
        _klss+=_bf.__class__.__name__.lower()
        attrs['class'] = "edit_%s" % _klss
        if getattr(_bf, 'extra_attrs', False):
            attrs['data-mce-config'] = json.dumps(getattr(_bf, 'extra_attrs', {}))
        #attrs = JEditableAttrsDict(attrs)
        return attrs

    def __init__(self, *args, **kwargs):
        super(JEditableMixin, self).__init__(*args, **kwargs)
        _cls_names = []
        for fld in self.fields:
            _form_field = self.fields[fld]
            if _form_field.widget.__class__.__name__ in (
                     'BootstrapRadioSelect', 'RadioSelect'):
                _form_field.widget = forms.Select(choices=_form_field.choices)
            _cls_name = _form_field.__class__.__name__
            if _cls_name not in _cls_names:
                _cls_names.append(_cls_name)
            if 'DateField' == _cls_name:
                _cls_names.append('datepicker')
                self.fields[fld].widget = forms.widgets.TextInput(attrs={'class': _cls_names, 'type':'date'})
            if not _form_field.show_hidden_initial:
                attrs = _form_field.widget.attrs
                widget_attrs = self.generate_jeditable_attrs(fld)
                attrs.update(widget_attrs)

                #if 'DateField' == _cls_name:
                #   attrs.update({'data-date':'2014-01-01'})
        # add media as required
        if not getattr(self.Media, 'js', False):
            self.Media.js = ()
            self.Media.css = {'screen': (),}
        if 'BooleanField' in _cls_names or 'NullBooleanField' in _cls_names:
            self.Media.js += (staticfiles_storage.url('common/js/jquery.icheck.min.js'),)
            self.Media.css['screen'] += (staticfiles_storage.url('common/css/icheck/skins/flat/blue.css'),)
        if 'ModelMultipleChoiceField' in _cls_names:
            self.Media.js += (staticfiles_storage.url('common/js/chosen.jquery.min.js'),)
            self.Media.css['screen'] += (staticfiles_storage.url('common/css/chosen.min.css'),)
        # prevent multiple media includes
        self.Media.js = tuple(set(self.Media.js))
        self.Media.css['screen'] = tuple(set(self.Media.css['screen']))


class JEditableFormMixin(JEditableMixin, forms.Form):
    pass


class JEditableModelForm(JEditableMixin,forms.ModelForm):
    pass

class CommentForm(BootstrapForm):
    comment = forms.CharField(widget=forms.Textarea)
