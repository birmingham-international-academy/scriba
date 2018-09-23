from scriba.settings.base import *


ENVIRONMENT = 'production'

DEBUG = True

ALLOWED_HOSTS = [
    '178.128.41.130',
    'englishapp.tk',
    'www.englishapp.tk'
]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
