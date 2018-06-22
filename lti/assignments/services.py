import urllib
import uuid
import hashlib
import requests
import base64
import time
import untangle
import xml.etree.ElementTree as xml
from xml.dom import minidom
from django.conf import settings
from lti.core.services import HmacSha1Signer
from lti.core.exceptions import OutcomeServiceParameterError, OutcomeServiceExtensionError
from lti.core.checker import Checker
from lti.core.interpreters import *
from html.parser import HTMLParser


class OutcomeDocument:
    def __init__(self, _type, source_did, outcome_service):
        self.source_did = source_did
        self.outcome_service = outcome_service
        self.has_payload = False

        self.doc = xml.Element('imsx_POXEnvelopeRequest')
        self.doc.set('xmlns', 'http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0')

        head_wrapper = xml.SubElement(self.doc, 'imsx_POXHeader')
        self.head = xml.SubElement(head_wrapper, 'imsx_POXRequestHeaderInfo')

        body_wrapper = xml.SubElement(self.doc, 'imsx_POXBody')
        type_wrapper = xml.SubElement(body_wrapper, _type + 'Request')
        self.body = xml.SubElement(type_wrapper, 'resultRecord')

        # Generate a unique identifier and
        # apply the version to the header information
        imsx_version = xml.SubElement(self.head, 'imsx_version')
        imsx_version.text = 'V1.0'
        imsx_message_identifier = xml.SubElement(self.head, 'imsx_messageIdentifier')
        imsx_message_identifier.text = str(uuid.uuid1())

        # Apply the source DID to the body
        sourced_guid = xml.SubElement(self.body, 'sourcedGUID')
        sourced_id = xml.SubElement(sourced_guid, 'sourcedId')
        sourced_id.text = source_did

        self.result = None

    def _result_element(self):
        if self.result is None:
            self.result = xml.SubElement(self.body, 'result')
        return self.result

    def _add_payload(self, _type, value):
        if self.has_payload:
            raise OutcomeServiceExtensionError('Result data payload has already been set')

        if self.outcome_service.supports_result_data(type):
            raise OutcomeServiceExtensionError('Result data type is not supported')

        result_element = self._result_element()
        result_data = xml.SubElement(result_element, 'resultData')
        result_data_type = xml.SubElement(result_data, _type)
        result_data_type.text = value
        self.has_payload = True

    def add_score(self, score, language):
        if (type(score) != int and type(score) != float) or score < 0 or score > 1.0:
            raise OutcomeServiceParameterError('Score must be a floating point number >= 0 and <= 1')

        result_element = self._result_element()
        result_score = xml.SubElement(result_element, 'resultScore')
        result_score_language = xml.SubElement(result_score, 'language')
        result_score_language.text = language
        result_score_text_string = xml.SubElement(result_score, 'textString')
        result_score_text_string.text = str(score)

    def add_text(self, text):
        self._add_payload('text', text)

    def add_url(self, url):
        self._add_payload('url', url)

    def finalize(self):
        string = xml.tostring(self.doc, 'utf-8') # Add <?xml version = "1.0" encoding = "UTF-8"?>
        reparsed = minidom.parseString(string)
        return reparsed.toprettyxml(indent="  ")


class OutcomeService:
    REQUEST_REPLACE = 'replaceResult'
    REQUEST_READ = 'readResult'
    REQUEST_DELETE = 'deleteResult'

    def __init__(self, options):
        self.consumer_key = options.get('consumer_key')
        self.consumer_secret = options.get('consumer_secret')
        self.service_url = options.get('service_url')
        self.source_did = options.get('source_did')
        self.result_data_types = options.get('result_data_types', [])
        self.signer = options.get('signer', HmacSha1Signer())
        self.cert_authority = options.get('cert_authority')
        self.language = options.get('language', 'en')

        self.service_url_parts = urllib.parse.urlparse(self.service_url)
        self.service_url_oauth = self.service_url_parts.scheme + '://' + self.service_url_parts.netloc + self.service_url_parts.path

    def _encode(self, string):
        return urllib.parse.quote(string, safe='~')

    def _encode_param(self, key, value):
        return key + '="' + self._encode(value) + '"'

    def _build_headers(self, body):
        headers = {
            'oauth_version': '1.0',
            'oauth_nonce': str(uuid.uuid4()),
            'oauth_timestamp': str(int(round(time.time()))),
            'oauth_consumer_key': self.consumer_key,
            'oauth_body_hash': base64.b64encode(hashlib.sha1(bytes(body, 'utf-8')).digest()), #crypto.createHash('sha1').update(body).digest('base64')
            'oauth_signature_method': 'HMAC-SHA1'
        }

        headers['oauth_signature'] = self.signer.build_signature_raw(
            self.service_url_oauth,
            self.service_url_parts,
            'POST',
            headers,
            self.consumer_secret
        )

        headersList = [self._encode_param(key, value) for key, value in headers.items()]

        return {
            'Authorization': 'OAuth realm="",' + ','.join(headersList),
            'Content-Type': 'application/xml'#,
            #'Content-Length': str(len(body))
        }

    def _send_request(self, doc):
        xmlDoc = doc.finalize()
        headers = self._build_headers(xmlDoc)

        r = requests.post(self.service_url, data=xmlDoc, headers=headers)

        # TODO: cert_authority

        tree_obj = untangle.parse(r.text)

        response = tree_obj.imsx_POXEnvelopeResponse
        code = response.imsx_POXHeader.imsx_POXResponseHeaderInfo.imsx_statusInfo.imsx_codeMajor.cdata
        status = True
        message = None

        if code != 'success':
            status = False
            message = response.imsx_POXHeader.imsx_POXResponseHeaderInfo.imsx_statusInfo.imsx_description.cdata

        return {
            'status': status,
            'message': message,
            'data': tree_obj
        }

    def supports_result_data(self, _type):
        return _type in self.result_data_types

    def send_replace_result(self, score):
        doc = OutcomeDocument(self.REQUEST_REPLACE, self.source_did, self)
        doc.add_score(score, self.language)
        return self._send_request(doc)

    def send_replace_result_with_text(self, score, text):
        doc = OutcomeDocument(self.REQUEST_REPLACE, self.source_did, self)
        doc.add_score(score, self.language)
        doc.add_text(text)
        return self._send_request(doc)

    def send_replace_result_with_url(self, score, url):
        doc = OutcomeDocument(self.REQUEST_REPLACE, self.source_did, self)
        doc.add_score(score, self.language)
        doc.add_url(url)
        return self._send_request(doc)

    def send_read_result(self):
        doc = OutcomeDocument(self.REQUEST_READ, self.source_did, self)
        response = self._send_request(doc)

        return float(response.get('data').imsx_POXBody.readResultResponse.result.resultScore.textString.cdata)

    def send_delete_result(self):
        doc = OutcomeDocument(self.REQUEST_DELETE, self.source_did, self)
        return self._send_request(doc)


class AssignmentDescriptionParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.excerpt = ''
        self.reference = ''
        self.in_excerpt = False
        self.in_reference = False

    def handle_data(self, data):
        _data = data.lower()

        if _data == 'excerpt':
            self.in_excerpt = True
            self.in_reference = False
        elif _data == 'reference':
            self.in_excerpt = False
            self.in_reference = True
        else:
            if self.in_excerpt:
                self.excerpt += data
            elif self.in_reference:
                self.reference += data


class AssignmentService:
    def __init__(self, assm_description, assm_type, assm_points_possible, service_url, source_did):
        self.type = assm_type
        self.points_possible = assm_points_possible
        self.outcome_service = OutcomeService({
            'consumer_key': settings.CANVAS['CONSUMER_KEY'],
            'consumer_secret': settings.CANVAS['SHARED_SECRET'],
            'service_url': service_url,
            'source_did': source_did,
            'result_data_types': ['text']
        })
        self._parse_description(assm_description)

    def _parse_description(self, description):
        parser = AssignmentDescriptionParser()
        parser.feed(description)

        self.excerpt = parser.excerpt.strip()
        self.reference = parser.reference.strip()

    def run_analysis(self, text):
        checker = Checker(text, self.excerpt, self.reference)
        interpreter = FeedbackInterpreter() if self.type == 'pilot' else GradeInterpreter(self.points_possible)

        data = checker.run()
        data['text'] = text
        data = interpreter.run(data)

        if self.type != 'pilot':
            self.send_grade(data)

        return data

    def send_grade(self, data):
        # TODO: Deduce points from data
        self.outcome_service.send_replace_result_with_text(data.get('score'), data.get('comments'))
