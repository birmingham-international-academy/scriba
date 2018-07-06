from scriba.settings.base import *


# local

ENVIRONMENT = 'local'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1'
]

INSTALLED_APPS = INSTALLED_APPS + [
    'sslserver'
]
