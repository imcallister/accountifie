"""
Adapted with permission from ReportLab's DocEngine framework
"""



# as this is in a models.py, it will get loaded at django server start
# it intends to fail 
"""
import os, sys
from django.conf import settings

tcp = settings.TEMPLATE_CONTEXT_PROCESSORS


if 'accountifie.common.views.base_templates' not in tcp:
    sys.stderr.write('''!!!
    You have upgrade DocEngine
    Please add:

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

    to your settings.py
''')
    os.kill(os.getpid(),9)
    sys.exit(1)
"""