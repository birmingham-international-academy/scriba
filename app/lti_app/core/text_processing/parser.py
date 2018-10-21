from nltk.tree import ParentedTree

from lti_app import strings
from lti_app.core.api import CoreNlpClient


class Parser:
    def __init__(self):
        self.client = CoreNlpClient()

    def parse(self, text):
        data = self.client.run(text, ['parse'])
        sentences = data.get('sentences')
        constituencies = []
        dependencies = []
        tagged_tokens = []

        for sentence in sentences:
            constituencies.append(ParentedTree.fromstring(sentence.get('parse')))
            dependencies.append(sentence.get('basicDependencies'))
            tagged_tokens.append(sentence.get('tokens'))

        return {
            strings.constituencies: constituencies,
            strings.dependencies: dependencies,
            strings.tagged_tokens: tagged_tokens
        }
