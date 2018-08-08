from lti_app.exceptions import BaseLtiException


class CitationException(BaseLtiException):
    def __init___(self, schema):
        BaseLtiException.__init__(self, schema)

    @staticmethod
    def generic():
        return CitationException({
            'code': 'CIT_GENERIC',
            'message': 'Generic citation error.'
        })

    @staticmethod
    def bad_format():
        return CitationException({
            'code': 'CIT_BAD_FORMAT',
            'message': 'Badly formatted citation.'
        })


class TextProcessingException(BaseLtiException):
    def __init__(self, schema):
        BaseLtiException.__init__(self, schema)

    @staticmethod
    def generic():
        return TextProcessingException({
            'code': 'TXT_GENERIC',
            'message': 'Generic text processing error.'
        })

    @staticmethod
    def missing_key(key):
        return TextProcessingException({
            'code': 'TXT_MISSING_KEY',
            'message': 'The document is missing the key: {}'.format(key)
        })

    @staticmethod
    def invalid_processor_type(accepted_type):
        return TextProcessingException({
            'code': 'TXT_INVALID_PROCESSOR_TYPE',
            'message': 'The supplied processor is not of type {}'.format(accepted_type.__name__)
        })
