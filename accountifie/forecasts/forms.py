import random

from django import forms

from betterforms.forms import Fieldset, BetterForm, BetterModelForm
from accountifie.toolkit.forms import JEditableMixin, BootstrapMixin, Html5Mixin, Html5ModelForm
from betterforms.changelist import SearchForm

from .models import Forecast
from accountifie.toolkit.utils import random_color
from accountifie.gl.models import Company


class ForecastForm(BootstrapMixin, JEditableMixin, Html5Mixin, BetterModelForm):

    class Meta:
        model = Forecast
        fieldsets = (
            Fieldset('', (
                ('label',),
                ('start_date',),
                ('comment',),
            )),
        )

    def __init__(self, *args, **kwargs):
        super(ForecastForm, self).__init__(*args, **kwargs)
        self.fields['label'].widget.attrs.update({'data-can_edit': 'false'})



class ForecastBetterForm(BootstrapMixin, Html5Mixin, BetterModelForm):

    class Meta:
        model = Forecast
        fieldsets = (
            Fieldset('', (
                Fieldset('', (
                ('label',),
                ('start_date',),
                ('comment',),
            )),
            )),
        )

    def __init__(self, *args, **kwargs):
        super(ForecastBetterForm, self).__init__(*args, **kwargs)
        instance = self.instance
        model = instance.__class__
        num = model.objects.count()


"""
class ForecastBaseForm(BootstrapMixin, Html5ModelForm):
    class Meta:
        model = Forecast
"""

class FileForm(forms.Form):
    file = forms.FileField(required=True)
    #Hidden by Andy, suggest to strip out all code.
    #check = forms.BooleanField(help_text='first check contents of the file', required=False)

