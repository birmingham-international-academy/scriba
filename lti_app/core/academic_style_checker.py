"""Provides academic style checkers.

Academic style checkers must check for informalities that
are not used in academic texts.
"""

import json
import os

import spacy
from nltk import pos_tag, tokenize
from nltk.stem import WordNetLemmatizer

from lti_app.core.text_helpers import TextProcessor
from lti_app.helpers import get_current_dir


class Checker(TextProcessor):
    """Implements the default academic style checker.

    Args:
        text (str): The text submitted by the student.
    """

    def __init__(self, text):
        self.text = text
        TextProcessor.__init__(self)

    def _load_tools(self):
        self.lemmatizer = WordNetLemmatizer()
        # self.nlp = spacy.load('en')  # en_core_web_sm.load()

    def _preprocess(self):
        self.tokens = tokenize.word_tokenize(self.text)
        self.tagged_tokens = pos_tag(self.tokens)
        self.lemmas = [
            self.lemmatizer.lemmatize(i, j[0].lower())
            if j[0].lower() in ['a', 'n', 'v']
            else self.lemmatizer.lemmatize(i)
            for i, j in self.tagged_tokens
        ]
        # self.doc = self.nlp(self.text)

    def get_phrasal_verbs(self):
        """Get the phrasal verbs.

        Returns:
            list of str: The phrasal verbs.
        """

        phrasal_verbs = []

        """
        for token in self.doc:
            if token.dep_ == 'prt' and token.head.pos_ == 'VERB':
                verb = token.head.orth_
                particle = token.orth_
                phrasal_verbs.append(verb + ' ' + particle)
        """

        return phrasal_verbs

    def get_contractions(self):
        """Get contractions such as `don't`

        Returns:
            list of str: The contractions.
        """

        return [
            self.tagged_tokens[index - 1][0] + token
            for index, (token, pos) in enumerate(self.tagged_tokens)
            if "'" in token and pos != 'POS'
        ]

    def get_general_informalities(self):
        """Get general informal words such as 'nice', 'good', 'bad'.

        Returns:
            list of str: General informalities.
        """

        lemmas = ' '.join(self.lemmas)
        current_dir = get_current_dir(__file__)
        filename = os.path.join(current_dir, 'data', 'informal.json')

        with open(filename, 'r') as f:
            informal_words = json.load(f)

            return [
                word
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
