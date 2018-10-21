import pytest

from .data import similarity_data
from .fixtures import make_semantics_checker


@pytest.mark.parametrize('text,excerpt,supporting_excerpts,threshold,expected', similarity_data)
def test_similarity(make_semantics_checker, text, excerpt, supporting_excerpts, threshold, expected):
    semantics_checker = make_semantics_checker(
        text,
        excerpt,
        supporting_excerpts
    )

    similarity = semantics_checker.run()

    assert (similarity > threshold) == expected
