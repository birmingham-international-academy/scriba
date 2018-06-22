import os
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from lti.helpers import get_current_dir, find_file


def load_stanford_parser():
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
