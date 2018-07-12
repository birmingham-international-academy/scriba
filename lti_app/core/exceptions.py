from lti_app.exceptions import BaseLtiException


class BadlyFormattedCitationException(BaseLtiException):
    def __init___(self):
        BaseLtiException.__init__(self, 'cc1')
