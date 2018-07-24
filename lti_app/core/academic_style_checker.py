"""Provides academic style checkers.

Academic style checkers must check for informalities that
are not used in academic texts.
"""

import json
import os

from lti_app.core.text_helpers import remove_stopwords
from lti_app.helpers import get_current_dir


class Checker:
    """Implements the default academic style checker.

    Args:
        text_document (Document): The text submitted by the student.
    """

    def __init__(self, text_document):
        self.text_document = text_document

    def get_phrasal_verbs(self):
        """Get the phrasal verbs.

        Returns:
            list of str: The phrasal verbs.
        """

        phrasal_verbs = []

        for token in self.text_document.get('spacy_doc'):
            if token.dep_ == 'prt' and token.head.pos_ == 'VERB':
                verb = token.head.orth_
                particle = token.orth_
                phrasal_verbs.append(verb + ' ' + particle)

        return phrasal_verbs

    def get_contractions(self):
        """Get contractions such as `don't`

        Returns:
            list of str: The contractions.
        """

        tagged_tokens = self.text_document.get('tagged_tokens')

        return [
            tagged_tokens[index - 1][0] + token
            for index, (token, pos) in enumerate(tagged_tokens)
            if "'" in token and pos != 'POS'
        ]

    def get_quotation_overuses(self):
        """Get quotation overuses.

        Returns:
            list of str: The quotation overuses.
        """
        # text = remove_stopwords(self.text)
        pass

    def get_general_informalities(self):
        """Get general informal words such as 'nice', 'good', 'bad'.

        Returns:
            list of str: General informalities.
        """

        lemmas = ' '.join(self.text_document.get('lemmas'))
        current_dir = get_current_dir(__file__)
        filename = os.path.join(current_dir, 'data', 'informal.json')

        with open(filename, 'r') as f:
            informal_words = json.load(f)

            return [
                word.get('entity')
                for word in informal_words
                if word.get('entity') in lemmas
            ]

    def run(self):
        """Run the checker.

        Returns:
            dict: The academic style check data using the described methods.
        """

        return {
            'phrasal_verbs': self.get_phrasal_verbs(),
            'contractions': self.get_contractions(),
            'general_informalities': self.get_general_informalities()
        }
