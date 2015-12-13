from django import forms

from betterforms.forms import Fieldset, BetterForm, BetterModelForm
from betterforms.changelist import SearchForm

from accountifie.toolkit.forms import BootstrapMixin, Html5Mixin


import models

class SplashForm(SearchForm):
    SEARCH_FIELDS = []
    def set_searchfields(self, fld_list):
        self.SEARCH_FIELDS = fld_list

    def __init__(self, *args, **kwargs):
        super(SplashForm, self).__init__(*args, **kwargs)
        

class GLSnapshotBetterForm(BootstrapMixin, Html5Mixin, BetterModelForm):

    class Meta:
        model = models.GLSnapshot
        fieldsets = (
            Fieldset('', (
                ('short_desc', 'closing_date', 'snapped_at'),
                ('comment',),
                
            )),
        )

    def __init__(self, *args, **kwargs):
        super(GLSnapshotBetterForm, self).__init__(*args, **kwargs)
        instance = self.instance
        model = instance.__class__
