
from betterforms.forms import Fieldset, BetterModelForm
from accountifie.toolkit.forms import JEditableMixin, BootstrapMixin, Html5Mixin

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
                ('model',),
                ('comment',),
            )),
        )

    def __init__(self, *args, **kwargs):
        super(ForecastForm, self).__init__(*args, **kwargs)
        self.fields['label'].widget.attrs.update({'data-can_edit': 'false'})
        self.fields['comment'].widget.attrs.update({'data-can_edit': 'false'})
