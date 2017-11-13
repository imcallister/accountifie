"""
from django import forms
from dal import autocomplete

from .models import Counterparty, Account


def counterparty_widget():
    return forms.ModelChoiceField(queryset=Counterparty.objects.all(),
      widget=autocomplete.ModelSelect2(url='counterparty-autocomplete')
                                  )

def account_widget():
    return forms.ModelChoiceField(queryset=Account.objects.all(),
                                  widget=autocomplete.ModelSelect2(url='account-autocomplete')
                                  )
"""
