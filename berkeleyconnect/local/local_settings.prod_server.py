from .settings import *
from django.conf.urls import include, url
import os

ALLOWED_HOSTS = ['.bearfounders.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'userdb',
        'USER': 'bearfounderadmin',
        'PASSWORD': 'audi2384',
        'HOST': 'bearfoundersusers.cdeuuniehauw.us-west-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# AWS Storage settings

AWS_STORAGE_BUCKET_NAME = 'bearfoundersfiles'

AWS_ACCESS_KEY_ID = 'AKIAI2V4635UQAPY4PJA'

AWS_SECRET_ACCESS_KEY = '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'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# This is used by the `static` template tag from `static`, if you're using that. Or if anything else
# refers directly to STATIC_URL. So it's safest to always set it.
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

STATICFILES_LOCATION = '/static/'

STATICFILES_STORAGE = 'custom_storages.StaticStorage'

STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)


# Tell the staticfiles app to use S3Boto storage when writing the collected static files (when
# you run `collectstatic`).
# STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = '/media/'

DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)


# Email settings

EMAIL_BACKEND = "mailer.backend.DbBackend"

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'noreply@bearfounders.com'

EMAIL_HOST = 'smtp.sendgrid.net'

EMAIL_HOST_USER = 'apikey'

EMAIL_HOST_PASSWORD = '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'

EMAIL_PORT = 587

ELASTIC_PREFIX = 'prod'