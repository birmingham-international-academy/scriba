import pytest

from lti_app.core.exceptions import TextProcessingException
from lti_app.core.text_processing.document import Document
from lti_app.core.text_processing.processing_graphs import (
    ProcessorNode,
    text_cleaner
)
from lti_app.core.text_processing.processors import TextProcessor


# Utility/Global Entities
# =============================================

class FullStopToCommaConverter(ProcessorNode):
    def __init__(self, name='fullstop2comma_converter', out='commatized'):
        ProcessorNode.__init__(self, name=name, out=out)

    def process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')
        cleaned_text = document.get(input_key)

        return cleaned_text.replace('.', ',')

fullstop2comma_converter = FullStopToCommaConverter()


# Data Providers
# =============================================

text_processing = [
    (
        '  The  education system   must be improved.  More investment is needed.',
        {
            text_cleaner: [fullstop2comma_converter],
            fullstop2comma_converter: []
        },
        text_cleaner,
        {
            'cleaned_text': 'The education system must be improved. More investment is needed.',
            'commatized': 'The education system must be improved, More investment is needed,'
        }
    )
]

processing_graphs = [
    (
        {
            text_cleaner: [fullstop2comma_converter],
            fullstop2comma_converter: []
        },
        text_cleaner
    )
]


# Tests
# =============================================

@pytest.mark.parametrize('text,graph,root,expected', text_processing)
def test_processing(text, graph, root, expected):
    text_processor = TextProcessor(graph, root)

    actual_document = text_processor.run(text)

    expected_document = Document(text, expected)

    assert actual_document == expected_document


@pytest.mark.parametrize('graph,root', processing_graphs)
def test_add_processor(graph, root):
    text_processor = TextProcessor(graph, root)

    # Already existent
    # ---------------------------------------------
    text_processor.add_processor(text_cleaner)
    assert len(text_processor) == 2

    # Not the same type
    # ---------------------------------------------
    with pytest.raises(TextProcessingException) as exc_info:
        text_processor.add_processor('Dummy node')
        assert 'TXT_INVALID_PROCESSOR_TYPE' == exc_info.code

    # Success
    # ---------------------------------------------
    node = ProcessorNode()
    text_processor.add_processor(node)

    assert node in text_processor
    assert text_processor[node] == []


@pytest.mark.parametrize('graph,root', processing_graphs)
def test_remove_processor(graph, root):
    text_processor = TextProcessor(graph, root)

    # Non-existent
    # ---------------------------------------------
    text_processor.remove_processor('Dummy node')
    assert len(text_processor) == 2

    # Remove leaf
    # ---------------------------------------------
    text_processor.remove_processor(fullstop2comma_converter)
    assert len(text_processor) == 1
    assert text_processor[root] == []

    # Remove root
    # ---------------------------------------------
    text_processor.remove_processor(root)
    assert len(text_processor) == 0
