"""Provides semantics checkers.

A semantic checker must detect the topic
as well as the semantic structure similarity.
"""

import os

import spacy
from gensim import corpora, models, similarities
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize

from lti_app.helpers import (
    get_current_dir, find_file, tok_and_lem, is_punctuation
)
from lti_app.core.text_helpers import load_stanford_parser, TextProcessor


class Checker(TextProcessor):
    """Implements the default semantics checker.

    Args:
        text (str): The text submitted by the student.
        excerpt (str): The assignment's excerpt.
    """

    def __init__(self, text, excerpt):
        self.text = text
        self.excerpt = excerpt
        TextProcessor.__init__(self)

    def _load_tools(self):
        _, self.dependency_parser = load_stanford_parser()
        self.nlp = spacy.load('en')

    def _preprocess(self):
        pass

    def _word_similarity(self, w1, w2):
        pass

    def run(self):
        pass
