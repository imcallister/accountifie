# Project project Django settings.
import os, sys, json, pandas


# stop those annoying warnings
pandas.options.mode.chained_assignment = None

PROJECT_NAME = 'accountifie'
PROJECT_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(PROJECT_DIR)

ENVIRON_DIR = os.path.realpath(os.path.join(PROJECT_DIR, '..'))

CLIENT_PROJECT = os.path.split(ENVIRON_DIR)[1]

DEBUG = False

DEFAULT_GL_STRATEGY = os.environ.get('DEFAULT_GL_STRATEGY', 'remote')


# end of over-rides for ansible lineinfile

TEMPLATE_DEBUG = False

ADMINS = (
    ('admin', 'test@accountifie.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'docengine_test.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ENVIRON_DIR, 'media')
DATA_ROOT = os.path.join(ENVIRON_DIR, 'data')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
DATA_URL = '/data/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ENVIRON_DIR, 'htdocs', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

PDFOUT_PATH = 'pdfout'
PDFOUT = os.path.join(DATA_ROOT, PDFOUT_PATH)


# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_=s8f!l_t=ys+nbm3q%08ew8zb(7bybf195*rl2dil87p197g$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.eggs.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accountifie.middleware.docengine.UserFindingMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accountifie.middleware.ssl.SSLRedirect',
    'accountifie.toolkit.error_handling.StandardExceptionMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "accountifie.common.views.base_templates",
    )


ROOT_URLCONF = PROJECT_NAME + '.urls'
WSGI_APPLICATION = PROJECT_NAME + '.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'djangosecure',
    #'cerberos',
    'accountifie.dashboard',

    'django_nose',
    'django_extensions',

    'betterforms',
    #'json_field',

    'accountifie.common',
    'accountifie.cal',
    'accountifie.gl',
    'accountifie.environment',

    'django_admin_bootstrapped',
    'django.contrib.admin',


)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s',
        },
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
            },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'database': {
            'level': 'INFO', # i.e., allows for logging messages of level INFO or higher
            'class': 'accountifie.common.log.DbLogHandler'
            }
        },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        'default': {
            'handlers': ['database',],
            'level': 'DEBUG',
            'propagate': True,
            },
        }
}


#From cerberos
MAX_FAILED_LOGINS = 5
MEMORY_FOR_FAILED_LOGINS = 3600  #try again an hour later

#from django-passwords
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = { "DIGITS": 1, "UPPER": 1 }

#uncomment this or put in your local settings if you want to save rml
SAVERML = os.path.join(PROJECT_DIR,'latest.rml')

TRACK_AJAX_CALLS = True

TESTING = 'test' in sys.argv

try:
    from localsettings import *
except ImportError:
    pass

#recommendations for security from: http://django-secure.readthedocs.org/en/v0.1.2/
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 24*24*3600*30
SECURE_HSTS_SECONDS_INCLUDE_SUBDOMAINDS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600

#avoids hourly logout when you're working
SESSION_SAVE_EVERY_REQUEST = True

from django.contrib import messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-debug',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger error'
    }



DASHBOARD_TITLE = CLIENT_PROJECT + ' Dashboard'
THUMBNAIL_SIZES = (
    (120,80),
    (240,160),
    (320,240),
    )


from datetime import date
DATE_EARLY = date(2013,1,1)  #before anything in your accounts system
DATE_LATE = date(2099,1,1)  #after anything in your accounts system
