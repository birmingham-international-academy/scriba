import dj_database_url

from scriba.settings.base import *


ENVIRONMENT = 'production'

DEBUG = True

ALLOWED_HOSTS = [
    '178.128.41.130',
    '.herokuapp.com'
]

"""
DATABASES['default'] = dj_database_url.config(
    default=os.environ.get('DATABASE_URL', '')
)
"""
