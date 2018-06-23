import urllib
import uuid
import hashlib
import requests
import base64
import time
import xml.etree.ElementTree as xml
from lti.tool_provider import ToolProvider
from django.conf import settings
from lti_app.core.checker import Checker
from lti_app.core.interpreters import *
from html.parser import HTMLParser


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
    def __init__(
            self, assm_description, assm_type,
            assm_points_possible, service_url, source_did):
        self.type = assm_type
        self.points_possible = assm_points_possible
        self.interpreter = (
            FeedbackInterpreter()
            if self.type == 'pilot'
            else GradeInterpreter(self.points_possible)
        )
        self.tool_provider = ToolProvider(
            consumer_key=settings.CANVAS['CONSUMER_KEY'],
            consumer_secret=settings.CANVAS['SHARED_SECRET'],
            params={
                'lis_outcome_service_url': service_url,
                'lis_result_sourcedid': source_did
            }
        )
        self._parse_description(assm_description)

    def _parse_description(self, description):
        parser = AssignmentDescriptionParser()
        parser.feed(description)

        self.excerpt = parser.excerpt.strip()
        self.reference = parser.reference.strip()

    def run_analysis(self, text):
        checker = Checker(text, self.excerpt, self.reference)
        data = checker.run()
        data['text'] = text
        data = self.interpreter.run(data)

        if self.type != 'pilot':
            self.send_grade(data)

        return data

    def send_grade(self, data):
        # TODO: Deduce points from data
        self.tool_provider.post_replace_result(
            data.get('score'),
            result_data={'text': data.get('comments')}
        )
