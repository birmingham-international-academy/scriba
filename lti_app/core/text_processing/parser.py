from nltk.tree import ParentedTree

from lti_app import strings
from lti_app.core.api import CoreNlpClient


class Parser:
    def __init__(self):
        self.client = CoreNlpClient()

    def parse(self, text):
        data = self.client.run(text, ['parse'])

        return [
            ParentedTree.fromstring(sentence.get('parse'))
            for sentence in data.get(strings.sentences)
        ]
