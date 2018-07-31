import pytest

from lti_app.core.text_processing.document import Document
from lti_app.core.text_processing.processing_graphs import (
    ProcessorNode,
    text_cleaner
)
from lti_app.core.text_processing.processors import TextProcessor


class FullStopToCommaConverter(ProcessorNode):
    def __init__(self, name='fullstop2comma_converter', out='commatized'):
        ProcessorNode.__init__(self, name=name, out=out)

    def process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')
        cleaned_text = document.get(input_key)

        return cleaned_text.replace('.', ',')


fullstop2comma_converter = FullStopToCommaConverter()


@pytest.mark.parametrize('text,graph,root,expected', [
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
])
def test_processing(text, graph, root, expected):
    text_processor = TextProcessor(graph, root)

    actual_document = text_processor.run(text)

    expected_document = Document(text, expected)

    assert actual_document == expected_document
