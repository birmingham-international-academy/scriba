"""Provides plagiarism checkers.

The minimum requirement of a plagiarism checker is to highlight
repeated word strings from two texts.
"""

from difflib import ndiff

from lti_app.core.text_helpers import TextProcessor
from lti_app.helpers import is_punctuation, tok_and_lem


class Checker(TextProcessor):
    """Implements the deafult plagiarism checker.

    Args:
        text (str): The text submitted by the student.
        excerpt (str): The assignment's excerpt.
    """

    def __init__(self, text, excerpt):
        self.text = text
        self.excerpt = excerpt
        TextProcessor.__init__(self)

    def _load_tools(self):
        pass

    def _preprocess(self):
        def get_lemmas(text):
            return [
                s.lower()
                for s in tok_and_lem(text)
                if not is_punctuation(s)
            ]

        self.text_lemmas = get_lemmas(self.text)
        self.excerpt_lemmas = get_lemmas(self.excerpt)

    def get_matches(self):
        """Get the diff matches.

        Returns:
            list of str: Similar strings using the diff tool.
        """

        matches = []
        match = []
        index = -1
        min_length = 4

        for i, d in enumerate(ndiff(self.text_lemmas, self.excerpt_lemmas)):
            if d[0] == ' ':
                word = d.split(' ')[-1]

                if i == index + 1:
                    match.append(word)
                else:
                    if len(match) >= min_length:
                        matches.append(' '.join(match))
                    match = [word]

                index = i

        if len(match) >= min_length:
            matches.append(' '.join(match))

        return matches

    def run(self):
        return self.get_matches()
