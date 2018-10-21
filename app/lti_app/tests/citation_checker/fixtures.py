import pytest

from lti_app.core.citation_checker import Checker as CitationChecker


@pytest.fixture
def make_citation_checker():
    def _make_citation_checker(text, reference):
        return CitationChecker(text, reference)

    return _make_citation_checker
