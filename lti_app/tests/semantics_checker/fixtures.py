import pytest

from lti_app.core.semantics_checker import Checker as SemanticsChecker
from lti_app.core.text_processing import processing_graphs, processors


@pytest.fixture
def make_semantics_checker():
    def _make_semantics_checker(text, excerpt, supporting_excerpts):
        text_processor = processors.TextProcessor(
            processing_graphs.default_graph,
            processing_graphs.text_cleaner
        )

        text_document = text_processor.run(text)
        excerpt_document = text_processor.run(excerpt)

        return SemanticsChecker(
            text_document,
            excerpt_document,
            supporting_excerpts
        )

    return _make_semantics_checker
