"""Provides text utilities."""

import os

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


class TextProcessor:
    """Abstract class for text processing."""

    def __init__(self):
        self._load_tools()
        self._preprocess()

    def _load_tools(self):
        raise NotImplementedError

    def _preprocess(self):
        raise NotImplementedError
