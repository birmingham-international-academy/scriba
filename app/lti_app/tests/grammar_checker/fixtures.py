import pytest

from lti_app.core.citation_checker import Checker as CitationChecker
from lti_app.core.grammar_checker import Checker as GrammarChecker
from lti_app.core.text_processing import processing_graphs, processors


@pytest.fixture
def make_grammar_checker():
    def _make_grammar_checker(
        text,
        reference='Test, T. (2018) "The test" Journal of Testing, 15(4): 261.'
    ):

        citation_checker = CitationChecker(text, reference)
        citation_check = citation_checker.run()

        text_processor = processors.TextProcessor(
            processing_graphs.default_graph,
            processing_graphs.citation_remover
        )
        document = text_processor.run(
            text,
            citation_check=citation_check
        )

        return GrammarChecker(document)

    return _make_grammar_checker
