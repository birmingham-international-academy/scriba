from urllib import parse
from base64 import b64encode
from hashlib import sha1
from oauthlib.oauth1 import RequestValidator
from django.conf import settings
import hmac


class CanvasService:
    @staticmethod
    def is_instructor(roles):
        roles = roles.lower().split(',')
        for role in roles:
            if role == 'instructor':
                return True
        return False


class ScribaRequestValidator(RequestValidator):
    @property
    def nonce_length(self):
        return 30, 45

    def validate_client_key(self, client_key, request):
        return client_key == settings.CANVAS['CONSUMER_KEY']

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                                     request, request_token=None,
                                     access_token=None):
        return True

    def get_client_secret(self, client_key, request):
        return settings.CANVAS['SHARED_SECRET']
