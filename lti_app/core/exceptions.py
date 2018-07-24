from lti_app.exceptions import BaseLtiException


class BadlyFormattedCitationException(BaseLtiException):
    def __init___(self):
        BaseLtiException.__init__(self, 'cit_check_1')


class PipelineException(BaseLtiException):
    def __init__(self):
        BaseLtiException.__init__(self, 'pipeline')
