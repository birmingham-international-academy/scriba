from lti_app.exceptions import BaseLtiException


class AssignmentException(BaseLtiException):
    code = 'ASM_GENERIC'
    description = 'Generic assignment error.'

    def __init___(self, code=None, description=None):
        BaseLtiException.__init__(self, code, description)

    @staticmethod
    def generic():
        return AssignmentException()

    @staticmethod
    def max_attempts_reached():
        return AssignmentException(
            code='CIT_MAX_ATTEMPTS_REACHED',
            description='The maximum number of attempts has been reached.'
        )
