"""Provides academic style checkers.

Academic style checkers must check for informalities that
are not used in academic texts.
"""

import json
import os
import re

from nltk import tokenize

from lti_app.core.text_helpers import remove_stopwords
from lti_app.core.text_processing.tools import Tools
from lti_app.helpers import get_current_dir


class Checker:
    """Implements the default academic style checker.

    Args:
        text_document (Document): The text submitted by the student.
    """

    def __init__(self, text_document):
        self.text_document = text_document
        self.enabled_checks = [
            'phrasal_verbs',
            'contractions',
            'quotation_overuses',
            'general_informalities'
        ]
        self.tools = Tools()

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

        tagged_tokens = [
            token
            for token in self.text_document.get('tagged_tokens')
            if token[0] != "''"
        ]

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
        text = self.text_document.get('cleaned_text')
        quotes_pattern = r'["\'](.*?)["\']'
        matches = re.findall(quotes_pattern, text)
        matches = [match.strip() for match in matches]
        quotation_overuses = []

        for match in matches:
            tokens = tokenize.word_tokenize(remove_stopwords(match))

            if len(tokens) > 2:
                quotation_overuses.append(match)

        return quotation_overuses

    def get_general_informalities(self):
        """Get general informal words such as 'nice', 'good', 'bad'.

        Returns:
            list of str: General informalities.
        """

        lemmas = ' '.join(
            [str(word_lemma[::-1])
            for word_lemma in self.text_document.get('lemmas')]
        )
        current_dir = get_current_dir(__file__)
        filename = os.path.join(
            current_dir, 'data', 'academic-style', 'informal-phrases.json'
        )

        with open(filename, 'r') as f:
            informal_phrases = json.load(f)
            informal_phrases_regexps = []

            for phrase in informal_phrases:
                regex = [
                    r'\([\'"]' + token + r'[\'"], [\'"](.+?)[\'"]\)'
                    for token in phrase.get('tokens')
                ]

                informal_phrases_regexps.append(' '.join(regex))

            matches = []
            for phrase_regex in informal_phrases_regexps:
                match = re.search(phrase_regex, lemmas, re.IGNORECASE)

                if match is not None:
                    tokens = list(match.groups())
                    phrase = self.tools.word_detokenizer.detokenize(tokens)
                    matches.append(phrase)

            return matches

    def run(self):
        """Run the checker.

        Returns:
            dict: The academic style check data using the described methods.
        """

        data = {}

        for check in self.enabled_checks:
            data[check] = getattr(self, 'get_' + check)()

        return data
