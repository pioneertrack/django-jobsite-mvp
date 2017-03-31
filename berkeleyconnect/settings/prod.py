from berkeleyconnect.settings.common import *

DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bearfoundersusers',
		'USER' : 'bearfounderadmin',
		'PASSWORD' : 'audi2384',
        'HOST' : 'bearfoundersusers.cdeuuniehauw.us-west-1.rds.amazonaws.com',
        'PORT' : '5432',
    }
}

INSTALLED_APPS += ('storages',)
AWS_STORAGE_BUCKET_NAME = "bearfoundersfiles"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
