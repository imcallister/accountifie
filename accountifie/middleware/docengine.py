"""
LoggingMiddleware used by Hilton and others to generate
our traditional log files and capture most details of the
request.

"""

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def getCurrentUser():
    "Call this from anywhere to get the user, assuming middleware below is installed"
    return getattr(_thread_locals, 'user', None)

def getCurrentRequest():
    "Call this from anywhere to get the request, assuming middleware below is installed"
    return getattr(_thread_locals, 'request', None)

class UserFindingMiddleware(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.request = request

from django.conf import settings
class ReplaceText(object):
    '''
    settings.TEXT_REPLACEMENTS = (
        'text0', 'replacement0',
        'text1', 'replacement1',
        ........
        'textn', 'replacementn',
        )
    replaces texti with replacementi in response.content

    *NB* this is not clever about substrings so do longer replacements first.
    '''
    def process_response(self, request, response):
        content = response.content
        TR = getattr(settings,'TEXT_REPLACEMENTS',())
        for i in range(0,len(TR),2):
            content = content.replace(TR[i],TR[i+1])
        response.content = content
        return response
