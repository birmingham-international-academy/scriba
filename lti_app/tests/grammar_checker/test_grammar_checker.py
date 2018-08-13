import pytest

from .data import comma_splices, noun_verb_disagreements, sentence_fragments
from .fixtures import make_grammar_checker


@pytest.mark.parametrize('text,expected', sentence_fragments)
def test_get_sentence_fragments(make_grammar_checker, text, expected):
    grammar_checker = make_grammar_checker(text)
    actions = [grammar_checker.get_sentence_fragments]

    data = grammar_checker.process_parse_tree(actions)
    sentence_fragments = data['sentence_fragments']

    assert sentence_fragments == expected


@pytest.mark.parametrize('text,expected', comma_splices)
def test_get_comma_splices(make_grammar_checker, text, expected):
    grammar_checker = make_grammar_checker(text)
    actions = [grammar_checker.get_comma_splices]

    data = grammar_checker.process_parse_tree(actions)
    comma_splices = data.get('comma_splices')

    assert comma_splices == expected


@pytest.mark.parametrize('text,expected', noun_verb_disagreements)
def test_get_noun_verb_disagreements(make_grammar_checker, text, expected):
    grammar_checker = make_grammar_checker(text)
    actions = [grammar_checker.get_noun_verb_disagreements]

    data = grammar_checker.process_parse_tree(actions)
    disagreements = data.get('noun_verb_disagreements')

    assert disagreements == expected
