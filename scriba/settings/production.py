import dj_database_url

from scriba.settings.base import *


ENVIRONMENT = 'production'

DEBUG = True

ALLOWED_HOSTS = ['.herokuapp.com']

DATABASES['default'] = dj_database_url.config(
    default=os.environ.get('DATABASE_URL', '')
)
