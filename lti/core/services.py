from urllib import parse
from base64 import b64encode
from hashlib import sha1
import hmac


class CanvasService:
    @staticmethod
    def is_instructor(roles):
        roles = roles.lower().split(',')
        for role in roles:
            if role == 'instructor':
                return True
        return False


class HmacSha1Signer:
    def _encode(self, string):
        return parse.quote(string, safe='~')

    def _encode_param(self, key, value):
        return key + '=' + self._encode(value)

    def _clean_request_body(self, data, query):
        out = []

        def clean_params(params):
            for key, values in params.items():
                if key == 'oauth_signature':
                    continue

                if type(values) is list:
                    for value in values:
                        out.append(self._encode_param(key, value))
                else:
                    out.append(self._encode_param(key, values))

        clean_params(data)
        clean_params(query)

        return self._encode('&'.join(sorted(out)))

    def sign_string(self, string, key, token):
        k = key + '&'
        k += ('' if token is None else token)
        h = hmac.new(bytes(k, 'ascii'), bytes(string, 'ascii'), sha1)
        return b64encode(h.digest()).decode()

    def build_signature_raw(self, req_url, parsed_url, method, data, consumer_secret, token = None):
        signature = [
            method.upper(),
            self._encode(req_url),
            self._clean_request_body(data, dict(parse.parse_qsl(parsed_url.query)))
        ]

        return self.sign_string('&'.join(signature), consumer_secret, token)

    def build_signature(self, request, data, consumer_secret, token = None):
        original_url = request.get_full_path()
        protocol = 'https'

        parsed_url = parse.urlparse(original_url)

        if data.get('tool_consumer_info_product_family_code') == 'canvas':
            original_url = parsed_url.path

        hit_url = protocol + '://' + request.get_host() + parsed_url.path

        return self.build_signature_raw(hit_url, parsed_url, request.method, data, consumer_secret, token)
