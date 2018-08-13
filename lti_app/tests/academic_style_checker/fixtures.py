import pytest

from lti_app.core.academic_style_checker import Checker as AcademicStyleChecker
from lti_app.core.text_processing import processing_graphs, processors


@pytest.fixture
def make_academic_style_checker():
    def _make_academic_style_checker(text):
        text_processor = processors.TextProcessor(
            processing_graphs.default_graph,
            processing_graphs.text_cleaner
        )
        text_processor.remove_processor(processing_graphs.parser)
        text_processor.add_channel(
            processing_graphs.text_cleaner,
            processing_graphs.spacy_processor
        )

        text_document = text_processor.run(text)

        return AcademicStyleChecker(text_document)

    return _make_academic_style_checker
