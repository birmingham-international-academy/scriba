import pytest

from .data import citation_check
from .fixtures import make_citation_checker


@pytest.mark.parametrize('text,reference,expected', citation_check)
def test_citation_check(make_citation_checker, text, reference, expected):
    citation_checker = make_citation_checker(text, reference)
    data = citation_checker.run()

    assert data.get('result') == expected.get('result')
    assert set(data.get('authors')) == set(expected.get('authors'))
    assert data.get('year') == expected.get('year')
    assert data.get('in_text') == expected.get('in_text')
    assert data.get('in_text_separated') == expected.get('in_text_separated')
    assert data.get('parenthetical') == expected.get('parenthetical')
