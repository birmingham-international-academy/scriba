import pytest

from lti_app.core.academic_style_checker import Checker as AcademicStyleChecker
from lti_app.core.text_processing import processing_graphs, processors


# Utility/Global Functions
# =============================================


def _get_academic_style_checker(text):
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


# Data Providers
# =============================================

phrasal_verbs_data = [
    (
        'The cat went to the garden. They left it out.',
        ['left out']
    ),
    (
        'Going down the mountain was hectic.',
        ['Going down']
    ),
    (
        'He got off at the airport. It was a rainy day. They switched the lights off.',
        ['got off', 'switched off']
    )
]


contractions_data = [
    (
        "I don't condone this behaviour!",
        ["don't"]
    ),
    (
        "Their fathers' cars were good.",
        []
    ),
    (
        "According to Keck, he won't allow the legislation to pass.",
        ["won't"]
    ),
    (
        "They should've gone to the park. It wasn't raining!",
        ["should've", "wasn't"]
    )
]


quotation_overuses_data = [
    (
        'According to Keck "high salt intake is dangerous".',
        ['high salt intake is dangerous']
    ),
    (
        'According to Keck the "triple effect" is going to be the normality.',
        []
    ),
    (
        "According to Keck 'high salt intake is dangerous'.",
        ['high salt intake is dangerous']
    )
]


general_informalities_data = [
    (
        "The test was good. There aren't many students.",
        ['good', "are n't many"]
    ),
    (
        "The test wasn't good. There weren't many students.",
        ['good', "were n't many"]
    )
]


# Tests
# =============================================

@pytest.mark.parametrize('text,expected', phrasal_verbs_data)
def test_phrasal_verbs_detection(text, expected):
    academic_style_checker = _get_academic_style_checker(text)

    actual = academic_style_checker.get_phrasal_verbs()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', contractions_data)
def test_contractions_detection(text, expected):
    academic_style_checker = _get_academic_style_checker(text)

    actual = academic_style_checker.get_contractions()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', quotation_overuses_data)
def test_quotation_overuses_detection(text, expected):
    academic_style_checker = _get_academic_style_checker(text)

    actual = academic_style_checker.get_quotation_overuses()

    assert set(actual) == set(expected)


@pytest.mark.parametrize('text,expected', general_informalities_data)
def test_general_informalities_detection(text, expected):
    academic_style_checker = _get_academic_style_checker(text)

    actual = academic_style_checker.get_general_informalities()

    print(actual)

    assert set(actual) == set(expected)
