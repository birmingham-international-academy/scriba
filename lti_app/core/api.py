"""Provides API clients."""

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
