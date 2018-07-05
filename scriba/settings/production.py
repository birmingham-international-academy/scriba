import dj_database_url

from scriba.settings.base import *


ENVIRONMENT = 'production'

DEBUG = False

ALLOWED_HOSTS = ['']

DATABASES['default'] = dj_database_url.config(
    default=''
)
