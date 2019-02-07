"""
Adapted with permission from ReportLab's DocEngine framework
"""



from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import TemplateView
import django.contrib.auth
from accountifie.common.forms import CommonAuthenticationForm, CommonPasswordChangeForm, \
        CommonPasswordResetForm, CommonSetPasswordForm
import accountifie.common.views

urlpatterns = [
    url(r'^login/$', accountifie.common.views.login, {
            'template_name': 'local_login.html',
            'authentication_form': CommonAuthenticationForm,
            #'SSL': True,
            }, name="accounts_login"
            ),
    url(r'^change_password/$', django.contrib.auth.password_change, {
            'template_name': 'password_change_form.html',
            'post_change_redirect': '/accounts/change_password/done/',
            'password_change_form': CommonPasswordChangeForm, 
            }, 
            name="change_password"
            ),
    url(r'^change_password/done/$', TemplateView.as_view(template_name='password_change_done.html',),),
    url(r'^logout/$', django.contrib.auth.logout, {'template_name': 'common/logout.html', }, 
            name="accounts_logout"
            ),
    url(r'^password_reset/$', django.contrib.auth.password_reset, {
            'template_name': 'accounts/password_reset_form.html',
            'email_template_name':'accounts/password_reset_email.html',
            'subject_template_name':'accounts/password_reset_subject.txt',
            'password_reset_form': CommonPasswordResetForm,
            'extra_context': {'REGISTER': 'docengine.register' in settings.INSTALLED_APPS}
            }, 
            name='password_reset'
            ),
    url(r'^password_reset_done/$', django.contrib.auth.password_reset_done, 
            {'template_name': 'accounts/password_reset_done.html',},
            name='password_reset_done'
            ),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
            django.contrib.auth.password_reset_confirm, 
            {'template_name': 'accounts/password_reset_confirm.html', 
                'set_password_form': CommonSetPasswordForm,},
            name='password_reset_confirm'
            ),
    url(r'^password_reset_complete/$', django.contrib.auth.password_reset_complete, 
        {'template_name': 'accounts/password_reset_complete.html',},
        name='password_reset_complete'),
]


