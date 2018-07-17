import dj_database_url

from scriba.settings.base import *


ENVIRONMENT = 'production'

DEBUG = False

ALLOWED_HOSTS = [
    '178.128.41.130',
    'englishapp.tk',
    'www.englishapp.tk',
    '.herokuapp.com'
]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

"""
DATABASES['default'] = dj_database_url.config(
    default=os.environ.get('DATABASE_URL', '')
)
"""
