'''
Simply pass 'SSL':True as a keyword argument from a url config and the user will
get redirected the same URL but on the https protocol.

E.g.
    urlpatterns = patterns('some_site.some_app.views', (r'^accounts/login/$','test_secure',{'SSL':True}), )
    
When you want to stop the secure session (e.g. when user logs out) just set
'SSL':True.

E.g.
    urlpatterns = patterns('some_site.some_app.views', (r'^accounts/logout/$','test_secure',{'SSL':False}), )

Original version:
    http://www.djangosnippets.org/snippets/85/

'''


__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

SSL = getattr(settings, 'DOCENGINE_SSL', 'SSL')
SECURE_PATHS = getattr(settings, 'DOCENGINE_SECURE_PATHS', ('/admin/', settings.LOGIN_URL))
HTTPS_SUPPORT = getattr(settings, 'DOCENGINE_HTTPS_SUPPORT', True)

class SSLRedirect:
    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            desiredSSL = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            desiredSSL = request.user.is_authenticated()
        """
        if not settings.DEVELOP:
            existingSSL = self._is_secure(request)
            if existingSSL != desiredSSL and HTTPS_SUPPORT:
                return self._redirect(request, desiredSSL)
        """
        
    def _is_secure(self, request):
        if request.is_secure():
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,request.get_host(),request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError("""Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs.""")

        return HttpResponsePermanentRedirect(newurl)



class SecureRequiredMiddleware(object):

    def __init__(self):
        self.paths = SECURE_PATHS 
        self.enabled = self.paths and HTTPS_SUPPORT and not settings.DEVELOP

    def process_request(self, request):
        if self.enabled and not request.is_secure():
            for path in self.paths:
                request_url = request.build_absolute_uri(request.get_full_path())
                if request.get_full_path().startswith(path) or \
                        path.startswith('http') and request_url.startswith(path): 
                        # just in case the paths are absolute URLs
                    secure_url = request_url.replace('http://', 'https://')
                    return HttpResponsePermanentRedirect(secure_url)
        return None
