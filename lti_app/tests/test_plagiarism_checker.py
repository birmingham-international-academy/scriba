import pytest

from lti_app.core.plagiarism_checker import Checker as PlagiarismChecker
from lti_app.core.text_processing import processing_graphs, processors


# Utility/Global Functions
# =============================================


def _get_plagiarism_checker(text, excerpt):
    text_processor = processors.TextProcessor(
        processing_graphs.default_graph,
        processing_graphs.text_cleaner
    )
    text_processor.remove_processor(processing_graphs.parser)

    text_document = text_processor.run(text)
    excerpt_document = text_processor.run(excerpt)

    return PlagiarismChecker(text_document, excerpt_document)


# Data Providers
# =============================================

plagiarism_data = [
    (
        'The cat went to the garden.',
        'The cat goes to the garden. He is a nice little animal',
        ['The cat went to the garden']
    ),
    (
        'Some words here. According to Keck having too much salt is bad.',
        'According to Keck having too much salt was bad in the past.',
        ['According to Keck having too much salt is bad']
    ),
    (
        'There is nothing wrong here. Not plagiarising at all!',
        'Look, I really think they are not plagiarising at all!',
        ['Not plagiarising at all']
    ),
    (
        'There is nothing wrong here. Not plagiarising at all!',
        'There is no plagiarism involved in the text of the student.',
        []
    )
]

# Tests
# =============================================

@pytest.mark.parametrize('text,excerpt,expected', plagiarism_data)
def test_plagiarism_check(text, excerpt, expected):
    plagiarism_checker = _get_plagiarism_checker(text, excerpt)

    actual = plagiarism_checker.run()

    assert actual == expected

