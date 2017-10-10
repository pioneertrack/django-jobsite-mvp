"""
Django settings for berkeleyconnect project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.contrib.messages import constants as message
from django.urls import reverse_lazy

PRODUCTION = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(p-162^r(zek4z#9_7i79@*9162c^(-26%@qe5vwvlvq4a^o=5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.bearfounders.com', '54.215.142.223']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'nocaptcha_recaptcha',
    'crispy_forms',
    'storages',
    'import_export',
    'django_extensions',
    'imagekit',
    'mailer',
    'django_elasticsearch_dsl',

    'landing',
    'website',
    'search',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'website.middleware.RemoveVaryCookiesMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.SessionHeaderMiddleware',
]

ROOT_URLCONF = 'berkeleyconnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.is_mobile',
                'website.context_processors.search_enabled',
                'website.context_processors.google_analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'berkeleyconnect.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '..', 'bower_components'),
)


# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'


# Authentication settings

AUTH_USER_MODEL = 'website.MyUser'

ACCOUNT_ACTIVATION_DAYS = 7

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = reverse_lazy('auth_login')

LOGIN_REDIRECT_URL = '/'


# Google recapcha settings

NORECAPTCHA_SITE_KEY = '6LfCyBUUAAAAALk0rgRTQB3W6Az4oOoTtifEkiAa'
NORECAPTCHA_SECRET_KEY = '6LfCyBUUAAAAAKUaBqh9zfDi7xtIOq5Oy8x7542D'


# Messages settings

MESSAGE_TAGS = {message.DEBUG: 'debug', message.INFO: 'info', message.SUCCESS: 'success', message.WARNING: 'warning', message.ERROR: 'danger'}


# Crispy template settings

CRISPY_TEMPLATE_PACK = 'bootstrap'

# Django-Mailer settings

MAILER_EMAIL_MAX_BATCH = 10

MAILER_EMAIL_MAX_DEFERRED = 5

MAILER_EMAIL_THROTTLE = 1

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

try:
  from .local_settings import *
except ImportError:
  pass
