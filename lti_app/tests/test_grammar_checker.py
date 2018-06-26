import pytest

from lti_app.core.grammar_checker import Checker


def _normalize_sentence(text):
    return text.split('.')[0].strip()


@pytest.mark.parametrize('text,expected', [
    (
        'A story with deep thoughts and emotions.',
        'A story with deep thoughts and emotions'
    ),
    (
        'I am going home. Which is why I left early.',
        'why I left early'
    ),
    (
        'Whereas he went to the garden.',
        'Whereas he went to the garden'
    )
])
def test_get_malformed_sentences(text, expected):
    grammar_checker = Checker(text)
    actions = [grammar_checker.get_malformed_sentences]

    data = grammar_checker.process_parse_tree(actions)
    malformed_sentences = data['malformed_sentences']

    assert _normalize_sentence(malformed_sentences[0]) == expected


@pytest.mark.parametrize('text,expected', [
    (
        'He are good.',
        ['He are']
    ),
    (
        'They is very nice. In fact the cat are great.',
        ['They is', 'cat are']
    )
])
def test_get_noun_verb_disagreements(text, expected):
    grammar_checker = Checker(text)
    actions = [grammar_checker.get_noun_verb_disagreements]

    data = grammar_checker.process_parse_tree(actions)
    disagreements = data.get('noun_verb_disagreements')

    assert disagreements == expected
