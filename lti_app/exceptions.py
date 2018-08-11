class BaseLtiException(Exception):
    code = None
    description = None

    def __init__(self, code=None, description=None):
        Exception.__init__(self)

        if code is not None:
            self.code = code

        if description is not None:
            self.description = description

    def __str__(self):
        code = self.code if self.code is not None else '???'
        return '%s: %s' % (code, self.description)

    def __repr__(self):
        code = self.code if self.code is not None else '???'
        return "<%s '%s'>" % (self.__class__.__name__, code)


class CachingException(BaseLtiException):
    code = 'CCH_GENERIC'
    description = 'Generic caching error.'

    def __init__(self, code=None, description=None):
        BaseLtiException.__init__(self, code, description)

    @staticmethod
    def generic():
        return CachingException()

    @staticmethod
    def not_cacheable():
        return CachingException(
            code='CCH_NOT_CACHEABLE',
            description='Object not cacheable.'
        )

    @staticmethod
    def invalid_key():
        return CachingException(
            code='CCH_INVALID_KEY',
            description='The key is invalid or it cannot be found.'
        )
