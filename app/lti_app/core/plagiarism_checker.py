"""Provides plagiarism checkers.

The minimum requirement of a plagiarism checker is to highlight
repeated word strings from two texts.
"""

import difflib
from difflib import ndiff

from lti_app import strings
from lti_app.core.text_processing.tools import Tools


class Checker:
    """Implements the deafult plagiarism checker.

    Args:
        text_document (Document): The text submitted by the student.
        excerpt_document (Document): The assignment's excerpt.
    """

    def __init__(self, text_document, excerpt_document):
        self.text_document = text_document
        self.excerpt_document = excerpt_document
        self.tools = Tools()

    def matches(self, list1, list2, min_length=4):
        words1, stems1 = [list(ls) for ls in list(zip(*list1))]
        words2, stems2 = [list(ls) for ls in list(zip(*list2))]

        stems1 = [lemma.lower() for lemma in stems1]
        stems2 = [lemma.lower() for lemma in stems2]

        while True:
            mbs = difflib.SequenceMatcher(None, stems1, stems2).get_matching_blocks()

            if len(mbs) == 1:
                break

            for i, j, n in mbs[::-1]:
                if n >= min_length:
                    yield words1[i: i + n]

                del words1[i: i + n]
                del stems1[i: i + n]
                del words2[j: j + n]
                del stems2[j: j + n]

    def run(self):
        text_stems = self.text_document.get(strings.stems)
        excerpt_stems = self.excerpt_document.get(strings.stems)
        matches = list(self.matches(text_stems, excerpt_stems))
        detokenize = self.tools.word_detokenizer.detokenize

        return [detokenize(match) for match in matches]
