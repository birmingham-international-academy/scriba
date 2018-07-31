from lti_app.exceptions import BaseLtiException


class BadlyFormattedCitationException(BaseLtiException):
    def __init___(self):
        BaseLtiException.__init__(self, 'cit_check_1')


class TextProcessingException(BaseLtiException):
    def __init__(self, message='Generic Text Processing Error.'):
        BaseLtiException.__init__(self, 'text_processing', {
            'message': message
        })
