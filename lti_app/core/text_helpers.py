"""Provides text utilities."""

import re
import os

from nltk.corpus import wordnet as wn
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser

from lti_app.helpers import find_file, get_current_dir


def load_stanford_parser():
    """Loads the Stanford parsers

    Returns:
        tuple: A tuple consisting of the Stanford Parser and
            the Stanford Dependency Parser
    """

    current_dir = get_current_dir(__file__)
    parser = 'stanford-parser'
    parser_jar = 'stanford-parser.jar'
    stanford_parser_dir = os.path.join(current_dir, 'data', parser)
    parser_jar_filename = os.path.join(stanford_parser_dir, parser_jar)
    models_jar_filename = find_file(
        'stanford-parser-*-models.jar',
        stanford_parser_dir,
        first=True
    )

    return (
        StanfordParser(parser_jar_filename, models_jar_filename),
        StanfordDependencyParser(parser_jar_filename, models_jar_filename)
    )


def clean_text(text):
    text = text.strip()
    text = re.sub(' +', ' ', text)
    text = re.sub('\n+', ' ', text)

    return text


def get_synonyms(word):
    return set([
        lemma
        for syn in wn.synsets(word)
        for lemma in syn.lemma_names()
    ])


def are_synonyms(word1, word2):
    syn_t = get_synonyms(word1)
    syn_e = get_synonyms(word2)
    synonyms = syn_t & syn_e

    return len(synonyms) > 0


def are_hierarchically_related(word1, word2):
    w2_hypernyms = set([h for s in wn.synsets(word2) for h in s.hypernyms()])
    w1_synsets = set(wn.synsets(word1))

    return len(w1_synsets & w2_hypernyms) > 0


class TextProcessor:
    """Abstract class for text processing."""

    def __init__(self):
        self._load_tools()
        self._preprocess()

    def _load_tools(self):
        raise NotImplementedError

    def _preprocess(self):
        raise NotImplementedError