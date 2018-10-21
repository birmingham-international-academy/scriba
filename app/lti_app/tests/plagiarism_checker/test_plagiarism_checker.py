import pytest

from .data import *
from .fixtures import make_plagiarism_checker


@pytest.mark.parametrize('text,excerpt,expected', plagiarism_data)
def test_plagiarism_check(make_plagiarism_checker, text, excerpt, expected):
    plagiarism_checker = make_plagiarism_checker(text, excerpt)

    actual = plagiarism_checker.run()

    assert actual == expected

