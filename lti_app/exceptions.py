class BaseLtiException(Exception):
    def __init___(self, code, context={}):
        message = 'Exception code: {}'.format(code)

        if len(context) > 0:
            message += '\nContext: {}'.format(context)

        Exception.__init__(self, "{}:{}".format(code, context))
        self.code = code
        self.context = context
