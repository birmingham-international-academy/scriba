from lti_app.exceptions import BaseLtiException


class CitationException(BaseLtiException):
    code = 'CIT_GENERIC'
    description = 'Generic citation error.'

    def __init___(self, code=None, description=None):
        BaseLtiException.__init__(self, code, description)

    @staticmethod
    def generic():
        return CitationException()

    @staticmethod
    def bad_format():
        return CitationException(
            code='CIT_BAD_FORMAT',
            description='Badly formatted citation.'
        )


class TextProcessingException(BaseLtiException):
    code = 'TXT_GENERIC'
    description = 'Generic text processing error.'

    def __init__(self, code=None, description=None):
        BaseLtiException.__init__(self, code, description)

    @staticmethod
    def generic():
        return TextProcessingException()

    @staticmethod
    def missing_key(key):
        return TextProcessingException(
            code='TXT_MISSING_KEY',
            description='The document is missing the key: {}'.format(key)
        )

    @staticmethod
    def invalid_processor_type(accepted_type):
        return TextProcessingException(
            code='TXT_INVALID_PROCESSOR_TYPE',
            description='The supplied processor is not of type {}'.format(accepted_type.__name__)
        )

    @staticmethod
    def invalid_graph():
        return TextProcessingException(
            code='TXT_INVALID_GRAPH',
            description='The processing graph is invalid.'
        )
