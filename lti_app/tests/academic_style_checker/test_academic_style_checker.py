import pytest

from .data import *
from .fixtures import make_academic_style_checker


@pytest.mark.parametrize('text,expected', phrasal_verbs_data)
def test_phrasal_verbs(make_academic_style_checker, text, expected):
    academic_style_checker = make_academic_style_checker(text)

    actual = academic_style_checker.get_phrasal_verbs()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', contractions_data)
def test_contractions(make_academic_style_checker, text, expected):
    academic_style_checker = make_academic_style_checker(text)

    actual = academic_style_checker.get_contractions()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', quotation_overuses_data)
def test_quotation_overuses(make_academic_style_checker, text, expected):
    academic_style_checker = make_academic_style_checker(text)

    actual = academic_style_checker.get_quotation_overuses()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', general_informalities_data)
def test_general_informalities(make_academic_style_checker, text, expected):
    academic_style_checker = make_academic_style_checker(text)

    actual = academic_style_checker.get_general_informalities()

    print(actual)

    assert set(actual) == set(expected)
