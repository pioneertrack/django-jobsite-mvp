from .settings import *
from django.conf.urls import include, url
import os

DEBUG = True

# TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['127.0.0.1']

# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.sqlite3',
#          'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#      }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bearfounders',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_HOST = 'localhost'

EMAIL_PORT = 1025

EMAIL_HOST_USER = ''

EMAIL_HOST_PASSWORD = ''

EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = 'webmaster@example.com'

if DEBUG:

    ALLOWED_DOMAINS = []

    INTERNAL_IPS = ['127.0.0.1']

    try:
        import debug_toolbar

        MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

        INSTALLED_APPS += ('debug_toolbar',)

        DEBUG_TOOLBAR_URLS = [url(r'^__debug__/', include(debug_toolbar.urls)), ]

    except ImportError:
        pass
