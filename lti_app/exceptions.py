class BaseLtiException(Exception):
    def __init___(self, code, context=None):
        message = 'Exception code: {}'.format(code)

        if context is None:
            context = {}

        if len(context) > 0:
            message += '\nContext: {}'.format(context)

        Exception.__init__(self, "{}:{}".format(code, context))
        self.code = code
        self.context = context
