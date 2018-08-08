class BaseLtiException(Exception):
    def __init___(self, schema):
        message = 'Exception Code: {}'.format(schema.get('code'))
        message += '\nMessage: {}'.format(schema.get('message'))

        Exception.__init__(self, message)

        self.code = schema.get('code')
        self.message = schema.get('message')


class CachingException(BaseLtiException):
    def __init__(self, schema):
        BaseLtiException.__init__(self, schema)

    @staticmethod
    def generic():
        return CachingException({
            'code': 'CCH_GENERIC',
            'message': 'Generic caching error.'
        })

    @staticmethod
    def not_cacheable():
        return CachingException({
            'code': 'CCH_NOT_CACHEABLE',
            'message': 'Object not cacheable.'
        })
