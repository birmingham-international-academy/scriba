"""Provides plagiarism checkers.

The minimum requirement of a plagiarism checker is to highlight
repeated word strings from two texts.
"""

from difflib import ndiff


class Checker:
    """Implements the deafult plagiarism checker.

    Args:
        text_document (Document): The text submitted by the student.
        excerpt_document (Document): The assignment's excerpt.
    """

    def __init__(self, text_document, excerpt_document):
        self.text_document = text_document
        self.excerpt_document = excerpt_document

    def get_matches(self):
        """Get the diff matches.

        Returns:
            list of str: Similar strings using the diff tool.
        """

        matches = []
        match = []
        index = -1
        min_length = 4

        text_lemmas = [lemma for _, lemma in self.text_document.get('lemmas')]
        excerpt_lemmas = [lemma for _, lemma in self.excerpt_document.get('lemmas')]

        for i, d in enumerate(ndiff(text_lemmas, excerpt_lemmas)):
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
