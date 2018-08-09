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
        {
            'authors': ['Edbali'],
            'year': '2018',
            'result': True,
            'in_text': True,
            'in_text_separated': False,
            'parenthetical': False
        }
    ),
    (
        'The cat is brown (Edbali 2018).',
        'Edbali, T. (2018) "The test" Journal of Testing, 15(4): 261-278.',
        {
            'authors': ['Edbali'],
            'year': '2018',
            'result': True,
            'in_text': False,
            'in_text_separated': False,
            'parenthetical': True
        }
    ),
    (
        'The cat is brown (Edbali).',
        'Edbali, T. (2018) "The test" Journal of Testing, 15(4): 261-278.',
        {
            'authors': ['Edbali'],
            'year': '2018',
            'result': False,
            'in_text': False,
            'in_text_separated': False,
            'parenthetical': False
        }
    ),
    (
        'The cat is brown (Edbali and Gazzini, 1999).',
        'Edbali, O. & Gazzini, T. (1999) The test.',
        {
            'authors': ['Edbali', 'Gazzini'],
            'year': '1999',
            'result': True,
            'in_text': False,
            'in_text_separated': False,
            'parenthetical': True
        }
    ),
    (
        'Edbali & Gazzini (1999) stated that the cat is brown.',
        'Edbali, O. and Gazzini, T. (1999) "The test"',
        {
            'authors': ['Edbali', 'Gazzini'],
            'year': '1999',
            'result': True,
            'in_text': True,
            'in_text_separated': False,
            'parenthetical': False
        }
    ),
    (
        'Edbali, Gazzini and Bona (1999) stated that the cat is brown.',
        'Edbali, O., Gazzini, T. and Bona, D. (1999) "The test"',
        {
            'authors': ['Edbali', 'Gazzini', 'Bona'],
            'year': '1999',
            'result': True,
            'in_text': True,
            'in_text_separated': False,
            'parenthetical': False
        }
    ),
    (
        'The cat is brown (Edbali et al. 1999).',
        'Edbali, O., Gazzini, T., Bona, D. and Buffon, G. (1999) "The test"',
        {
            'authors': ['Edbali', 'Gazzini', 'Bona', 'Buffon'],
            'year': '1999',
            'result': True,
            'in_text': False,
            'in_text_separated': False,
            'parenthetical': True
        }
    ),
    (
        'Edbali, in his 1999 article, stated that salt is bad for the health.',
        'Edbali, O. (1999) "The test"',
        {
            'authors': ['Edbali'],
            'year': '1999',
            'result': True,
            'in_text': False,
            'in_text_separated': True,
            'parenthetical': False
        }
    ),
    (
        'Gazzini ( 2017 ), stated that salt is bad for the health.',
        'Gazzini, T. (2017) "The test"',
        {
            'authors': ['Gazzini'],
            'year': '2017',
            'result': True,
            'in_text': True,
            'in_text_separated': False,
            'parenthetical': False
        }
    ),
    (
        'Salt is bad for your health (Edbali, Gazzini and Bona ,  1999).',
        'Edbali, O., Gazzini, T. and Bona, D. (1999) "The test"',
        {
            'authors': ['Edbali', 'Gazzini', 'Bona'],
            'year': '1999',
            'result': True,
            'in_text': False,
            'in_text_separated': False,
            'parenthetical': True
        }
    ),
]


# Tests
# =============================================

@pytest.mark.parametrize('text,reference,expected', citation_check)
def test_citation_check(text, reference, expected):
    citation_checker = _get_citation_checker(text, reference)
    data = citation_checker.run()

    print('ACTUAL:')
    print(data)
    print('EXPECTED:')
    print(expected)

    assert data.get('result') == expected.get('result')
    assert set(data.get('authors')) == set(expected.get('authors'))
    assert data.get('year') == expected.get('year')
    assert data.get('in_text') == expected.get('in_text')
    assert data.get('in_text_separated') == expected.get('in_text_separated')
    assert data.get('parenthetical') == expected.get('parenthetical')
