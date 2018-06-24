"""Provides core services for the LTI."""

from django.conf import settings
from oauthlib.oauth1 import RequestValidator


class ScribaRequestValidator(RequestValidator):
    """OAuth 1.0 request validator for Scriba."""

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
