from __future__ import absolute_import
# settings_test.py
from astrometry.net.settings_common import *

ENABLE_SOCIAL = False

# Since this settings file is only for testing, disable the host restriction here to ensure a smooth deployment
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://xxk.yage.ai']
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = 'django.sqlite3'


