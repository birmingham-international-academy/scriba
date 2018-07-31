import pytest

from lti_app.core.citation_checker import Checker as CitationChecker


# Utility/Global Functions
# =============================================

def _get_citation_checker(text, reference):
    return CitationChecker(text, reference)


# Data Providers
# =============================================

citation_check = [
    (
        'Edbali (2018) stated something.',
        'Edbali, T. (2018) "The test" Journal of Testing, 15(4): 261-278.',
        {'authors': ['Edbali'], 'year': '2018', 'result': True}
    ),
    (
        'The cat is brown (Edbali 2018).',
        'Edbali, T. (2018) "The test" Journal of Testing, 15(4): 261-278.',
        {'authors': ['Edbali'], 'year': '2018', 'result': True}
    ),
    (
        'The cat is brown (Edbali).',
        'Edbali, T. (2018) "The test" Journal of Testing, 15(4): 261-278.',
        {'authors': ['Edbali'], 'year': '2018', 'result': False}
    ),
    (
        'The cat is brown (Edbali and Gazzini, 1999).',
        'Edbali, O. and Gazzini, T. (1999) The test.',
        {'authors': ['Edbali', 'Gazzini'], 'year': '1999', 'result': True}
    ),
    (
        'Edbali & Gazzini (1999) stated that the cat is brown.',
        'Edbali, O. & Gazzini, T. (1999) "The test"',
        {'authors': ['Edbali', 'Gazzini'], 'year': '1999', 'result': True}
    ),
    (
        'Edbali, Gazzini and Bona (1999) stated that the cat is brown.',
        'Edbali, O., Gazzini, T. and Bona, D. (1999) "The test"',
        {'authors': ['Edbali', 'Gazzini', 'Bona'], 'year': '1999', 'result': True}
    ),
    (
        'The cat is brown (Edbali et al. 1999).',
        'Edbali, O., Gazzini, T., Bona, D. and Buffon, G. (1999) "The test"',
        {'authors': ['Edbali', 'Gazzini', 'Bona', 'Buffon'], 'year': '1999', 'result': True}
    )
]


# Tests
# =============================================

@pytest.mark.parametrize('text,reference,expected', citation_check)
def test_citation_check(text, reference, expected):
    citation_checker = _get_citation_checker(text, reference)
    data = citation_checker.run()

    assert data.get('result') == expected.get('result')
    assert set(data.get('authors')) == set(expected.get('authors'))
    assert data.get('year') == expected.get('year')
