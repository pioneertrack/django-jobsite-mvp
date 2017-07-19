from .settings import *
from django.conf.urls import include, url
import os

DEBUG = True

# TEMPLATE_DEBUG = DEBUG

# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.sqlite3',
#          'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#      }
# }

ALLOWED_HOSTS = ['.bearfounders.com', '54.215.142.223', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'userdb',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '..', 'bower_components'),
)

# STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'pipeline.finders.FileSystemFinder',
)
#
# PIPELINE = {
#     'PIPELINE_ENABLED': True,
#     'JS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
#     'JAVASCRIPT': {
#         'components': {
#             'source_filenames': (
#                 'bower_components/jquery/dist/jquery.min.js',
#                 'bower_components/bootstrap/dist/js/bootstrap.min.js',
#             ),
#             'output_filename': 'js/components.js',
#         }
#     }
# }

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

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

