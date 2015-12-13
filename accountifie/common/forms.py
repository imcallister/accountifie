"""
Adapted with permission from ReportLab's DocEngine framework
"""



import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, \
        PasswordResetForm, SetPasswordForm

from accountifie.toolkit.forms import BootstrapMixin


class CommonAuthenticationForm(BootstrapMixin, AuthenticationForm):
    """
    adding attrs towards bootstrap ui
    """
    bs_horizontal = False

    def __init__(self, request=None, *args, **kwargs):
        super(CommonAuthenticationForm, self).__init__(request=request, *args, **kwargs)

        #apps with self registration are email only.

        if getattr(settings, 'DOCENGINE_REGISTRATION', False) and getattr(settings, 'REGISTRATION_OPEN', False):
            _user_label = _user_placeholder = "Email"
        else:
            _user_label = 'ID'
            _user_placeholder = 'Email or Username'
        _usr_kls = self.fields['username'].widget.attrs.get('class','')
        if len(_usr_kls)>0:
            _usr_kls+=' '
        _passwd_kls = self.fields['password'].widget.attrs.get('class','')
        if len(_passwd_kls)>0:
            _passwd_kls+=' '
        self.fields['username'].label = _user_label
        self.fields['username'].widget.attrs.update({'class': _usr_kls+'input-block-level',
                                                     'placeholder': _user_placeholder})
        self.fields['password'].widget.attrs.update({'class':_usr_kls+'input-block-level', 
                                                     'placeholder':'Password '})


class MultiCommonAuthenticationForm(CommonAuthenticationForm):

    subdomain = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)

    def __init__(self, request=None, *args, **kwargs):
        super(MultiCommonAuthenticationForm, self).__init__(request=request, *args, **kwargs)
        _referer = request.META.get('HTTP_REFERER', '')
        if _referer:
            _referer = '/'.join(_referer.split('/', 3))
        if request and hasattr(request, 'session') and 'subdomain' in request.session:
            self.fields['subdomain'].initial = request.session['subdomain']
        elif _referer not in settings.LOGIN_URL:
            self.fields['subdomain'].initial=_referer.split('/')[-1]
        elif os.environ.get('DOMAIN', False):
            self.fields['subdomain'].initial = os.environ['DOMAIN']


class CommonPasswordChangeForm(BootstrapMixin, PasswordChangeForm):

    pass


class CommonPasswordResetForm(BootstrapMixin, PasswordResetForm):

    pass


class CommonSetPasswordForm(BootstrapMixin, SetPasswordForm):

    pass

