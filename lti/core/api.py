import requests
import xml.etree.ElementTree as ET
from django.conf import settings

class CanvasApiClient:
    def __init__(self):
        self.endpoint = 'https://canvas.bham.ac.uk/api/v1'

    def get_assignment(self, course_id, assignment_id):
        url = self.endpoint + '/courses/' + course_id + '/assignments/' + assignment_id
        headers = {'Authorization': 'Bearer ' + settings.CANVAS['PERSONAL_ACCESS_TOKEN']}

        return requests.get(url, headers=headers)

class FreeCiteApiClient:
    def __init__(self):
        self.endpoint = 'http://freecite.library.brown.edu/citations/create'

    def _gettext(self, citation, tag):
        if citation.find(tag) is not None:
            return citation.find(tag).text
        else:
            return ''

    def parse(self, citation_string):
        r = requests.post(self.endpoint, data={'citation' : citation_string}, headers={'Accept': 'text/xml'} )

        etree = ET.fromstring(r.text.encode('utf-8'))

        citation = etree.find('citation')

        return {
            'authors': [a.text for a in citation.iter('author')],
            'title': self._gettext(citation, 'title'),
            'journal': self._gettext(citation, 'journal'),
            'volume': self._gettext(citation, 'volume'),
            'pages': self._gettext(citation, 'pages'),
            'year': self._gettext(citation, 'year'),
            'raw_string': self._gettext(citation, 'raw_string')
        }
