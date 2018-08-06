"""Provides API clients."""

import json
import xml.etree.ElementTree as ET

import requests
from django.conf import settings


class CanvasApiClient:
    """The Canvas LMS API client"""

    def __init__(self):
        self.endpoint = 'https://canvas.bham.ac.uk/api/v1'

    def get_assignment(self, cid, aid):
        """Get an assignment object.

        Args:
            cid (str): The course ID.
            aid (str): The assignment ID.

        Returns:
            requests.Response: The HTTP response.
        """

        url = self.endpoint + '/courses/' + cid + '/assignments/' + aid
        access_token = settings.CANVAS['PERSONAL_ACCESS_TOKEN']
        headers = {'Authorization': 'Bearer ' + access_token}

        return requests.get(url, headers=headers)


class CoreNlpClient:
    def __init__(self):
        port = settings.STANFORD_CORENLP['PORT']
        self.endpoint = 'http://localhost:{0}'.format(port)

    def run(self, text, annotators):
        params = {
            'properties': json.dumps({
                'annotators': ','.join(annotators),
                'outputFormat': 'json'
            })
        }

        text = text.encode('utf-8')

        response = requests.post(self.endpoint, data=text, params=params)

        return response.json()


class LanguageToolClient:
    def __init__(self):
        port = settings.LANGUAGETOOL['PORT']
        self.endpoint = 'http://localhost:{0}/v2/check'.format(port)

    def check(self, text):
        response = requests.post(self.endpoint, data={
            'text': text,
            'language': 'en-GB',
            'disabledRules': 'EN_QUOTES',
        })

        return response.json().get('matches', [])
