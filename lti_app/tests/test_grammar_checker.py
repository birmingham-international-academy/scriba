import pytest

from lti_app.core.citation_checker import Checker as CitationChecker
from lti_app.core.grammar_checker import Checker as GrammarChecker
from lti_app.core.text_processing import processing_graphs, processors


# Utility/Global Functions
# =============================================

def _get_grammar_checker(
    text,
    reference='Test, T. (2018) "The test" Journal of Testing, 15(4): 261-278.'
):
    citation_checker = CitationChecker(text, reference)
    citation_check = citation_checker.run()

    text_processor = processors.TextProcessor(
        processing_graphs.default_graph,
        processing_graphs.citation_remover
    )
    document = text_processor.run(
        text,
        authors=citation_check.get('authors'),
        year=citation_check.get('year')
    )

    return GrammarChecker(document)


# Data Providers
# =============================================

sentence_fragments = [
    (
        'A story with deep thoughts and emotions.',
        ['A story with deep thoughts and emotions.']
    ),
    (
        'Whereas he went to the garden.',
        ['Whereas he went to the garden.']
    ),
    (
        'The cat.',
        ['The cat.']
    ),
    (
        'Whichever assignment.',
        []
    ),
    (
        'The university offers good courses. Such as electrical, chemical, and industrial engineering.',
        ['Such as electrical, chemical, and industrial engineering.']
    )
]

comma_splices = [
    (
        'Jim usually gets on with everybody, he is an understanding person.',
        ['Jim usually gets on with everybody, he is an understanding person.']
    ),
    (
        'Jim usually gets on with everybody; he is an understanding person.',
        []
    ),
    (
        'The students performed well, they are very motivated.',
        ['The students performed well, they are very motivated.']
    )
]

noun_verb_disagreements = [
    (
        'He are good.',
        ['He are good']
    ),
    (
        'They is very nice. In fact the cat are great.',
        ['They is very nice', 'the cat are great']
    ),
    (
        'I goes to the garden.',
        ['I goes to the garden']
    ),
    (
        'I go to the pitch. However they go to the market.',
        []
    ),
    (
        'Jordan, Michael, and John run and plays. They are good kids.',
        ['Jordan, Michael, and John run and plays']
    ),
    (
        'Jordan and John report that they acquired a plagiarism detection system which gives good results.',
        []
    ),
    (
        'The plagiarism detection system are efficient.',
        ['The plagiarism detection system are efficient']
    )
]


# Tests
# =============================================

@pytest.mark.parametrize('text,expected', sentence_fragments)
def test_get_sentence_fragments(text, expected):
    grammar_checker = _get_grammar_checker(text)
    actions = [grammar_checker.get_sentence_fragments]

    data = grammar_checker.process_parse_tree(actions)
    sentence_fragments = data['sentence_fragments']

    assert sentence_fragments == expected


@pytest.mark.parametrize('text,expected', comma_splices)
def test_get_comma_splices(text, expected):
    grammar_checker = _get_grammar_checker(text)
    actions = [grammar_checker.get_comma_splices]

    data = grammar_checker.process_parse_tree(actions)
    comma_splices = data.get('comma_splices')

    assert comma_splices == expected


@pytest.mark.parametrize('text,expected', noun_verb_disagreements)
def test_get_noun_verb_disagreements(text, expected):
    grammar_checker = _get_grammar_checker(text)
    actions = [grammar_checker.get_noun_verb_disagreements]

    data = grammar_checker.process_parse_tree(actions)
    disagreements = data.get('noun_verb_disagreements')

    assert disagreements == expected
