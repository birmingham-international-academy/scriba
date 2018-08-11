from lti_app.exceptions import BaseLtiException


class AssignmentException(BaseLtiException):
    def __init___(self, schema):
        BaseLtiException.__init__(self, schema)

    @staticmethod
    def generic():
        return AssignmentException({
            'code': 'ASM_GENERIC',
            'message': 'Generic assignment error.'
        })

    @staticmethod
    def max_attempts_reached():
        return AssignmentException({
            'code': 'CIT_MAX_ATTEMPTS_REACHED',
            'message': 'The maximum number of attempts has been reached.'
        })
