"""
Django settings for scriba project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json
# from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(
            os.path.join(__file__, '..')
        )
    )
)

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path, override=True)

# Application definition

INSTALLED_APPS = [
    'lti_app.apps.LtiConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lti_app.launch.middleware.ValidLaunchMiddleware',
]

ROOT_URLCONF = 'scriba.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'lti_app', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scriba.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432')
    }
}

# Logging
# https://docs.djangoproject.com/en/2.0/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "rq_console": {
            "level": "INFO",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        }
    },
    'loggers': {
        "rq.worker": {
            "handlers": ["rq_console"],
            "level": "INFO"
        },
    }
}

# Caching
# https://docs.djangoproject.com/en/2.0/topics/cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': None,
        'OPTIONS': {
            'binary': True,
            'behaviors': {
                'ketama': True,
            }
        }
    }
}

# Django-RQ
# https://github.com/rq/django-rq

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0
    }
}

RQ_EXCEPTION_HANDLERS = [
    'lti_app.rq_exception_handlers.inflate_exception',
    'lti_app.rq_exception_handlers.move_to_failed_queue'
]


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Application settings

SECRET_KEY = os.environ.get('SECRET_KEY')

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

CANVAS = {
    'CONSUMER_KEY': os.environ.get('CANVAS_CONSUMER_KEY'),
    'SHARED_SECRET': os.environ.get('CANVAS_SHARED_SECRET'),
    'PERSONAL_ACCESS_TOKEN': os.environ.get('CANVAS_PERSONAL_ACCESS_TOKEN'),
    'DEVELOPER_KEY': os.environ.get('CANVAS_DEVELOPER_KEY')
}

LANGUAGETOOL = {
    'PORT': os.environ.get('LANGUAGETOOL_PORT', '8081')
}

STANFORD_CORENLP = {
    'PORT': os.environ.get('STANFORD_CORENLP_PORT', '9000')
}
