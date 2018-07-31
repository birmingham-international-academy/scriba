import pytest

from lti_app.core.semantics_checker import Checker as SemanticsChecker
from lti_app.core.text_processing import processing_graphs, processors


# Utility/Global Functions
# =============================================

def _get_semantics_checker(text, excerpt, supporting_excerpts):
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


# Tests
# =============================================

@pytest.mark.parametrize('text,excerpt,supporting_excerpts,expected', [
    (
        "History has a habit of repeating itself through the decades in Europe. In Italy, where communists once held sway, nationalists are now in the ascendancy.",
        'In Italy communists once held sway, however nationalists are rising up.',
        [],
        True
    ),
    (
        'Paraphrasing has the essential function of helping the writer to restate the thoughts of another author without replicating them in an exact manner.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        [],
        True
    ),
    (
        'Paraphrasing has the essential function of helping the writer to restate the thoughts of another author without replicating them in an exact manner.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        ['Helping one writer to express the ideas of another using different words is a key feature in paraphrase.'],
        True
    ),
    (
        'An essential task of the paraphrase is to aid a writer in reformulating the thoughts of another author without exact copying.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        [],
        True
    ),
    (
        'Nationalists are repeating history by destroying communism.',
        'History repeats itself throughout the decades in Europe. For example, in Italy the nationalists have risen from a past of communism. Nationalist sentiment is a common feeling in the European Union.',
        [],
        False
    ),
    (
        'Keck (2006) mentions the important role that paraphrase plays in enabling writers to express the ideas of others in their own words.',
        'One important function of the paraphrase is to help a writer restate another author’s ideas without copying them exactly.',
        [],
        True
    )
])
def test_similarity(text, excerpt, supporting_excerpts, expected):
    semantics_checker = _get_semantics_checker(
        text,
        excerpt,
        supporting_excerpts
    )

    threshold = 0.15
    similarity = semantics_checker.run()

    assert (similarity > threshold) == expected
