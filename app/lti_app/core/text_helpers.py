"""Provides text utilities."""

import os
import re
import string

from django.conf import settings
from nltk import WhitespaceTokenizer
from nltk.corpus import stopwords, wordnet as wn
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser


def load_stanford_parser():
    """Loads the Stanford parsers

    Returns:
        tuple: A tuple consisting of the Stanford Parser and
            the Stanford Dependency Parser
    """

    version = '3.9.1'
    stanford_parser_dir = os.path.join(
        settings.BASE_DIR,
        'lti_app',
        'core',
        'data',
        'stanford-parser'
    )
    parser_jar_filename = os.path.join(
        stanford_parser_dir,
        'stanford-parser.jar'
    )
    models_jar_filename = os.path.join(
        stanford_parser_dir,
        'stanford-parser-' + version + '-models.jar'
    )

    return (
        StanfordParser(parser_jar_filename, models_jar_filename),
        StanfordDependencyParser(parser_jar_filename, models_jar_filename)
    )


def clean_text(text):
    text = text.strip()

    # Remove unnecessary spaces
    text = re.sub(' +', ' ', text)
    text = re.sub('\n+', ' ', text)

    # Add spaces for parenthesis
    text = re.sub(r'(\S)([\(\{\[])', r'\1 \2', text)
    text = re.sub(r'([\)\}\]])(\S)', r'\1 \2', text)

    # Add space after punctuation
    text = re.sub(r'([?.,!])(\S)', r'\1 \2', text)

    # Remove space before punctuation
    text = re.sub(r'\s([?.,!])', r'\1', text)

    return text


def is_punctuation(s):
    """Checks if the input string is a punctuation character.

    Args:
        s (str): The string.

    Returns:
        bool: Whether the string contains a punctuation character.
    """

    return s in string.punctuation


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


def remove_punctuation(s):
    """Remove punctuation from an input string.

    Args:
        s (str): The string to remove punctuation from.

    Returns:
        str: The string without punctuation.
    """

    return ''.join(c for c in s if c not in '!?.,;:')


def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    tokenizer = WhitespaceTokenizer()

    tokens = tokenizer.tokenize(text)
    filtered_text = [word for word in tokens if not word in stop_words]

    return ' '.join(filtered_text)
