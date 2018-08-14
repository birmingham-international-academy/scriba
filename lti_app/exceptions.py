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
