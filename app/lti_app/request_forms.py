from .exceptions import BaseLtiException


class BaseRequestForm:
    default_str = 'default'
    get_str = 'get'
    required_str = 'required'
    type_str = 'type'
    types = {
        'bool': [True, False, 1, 0, '1', '0', 'on', 'off', None, 'yes', 'no']
    }

    def __init__(self, form_data):
        self.form_data = form_data
        self.errors = []

    def validate(self):
        data = self.get_data()

        if len(self.errors) > 0:
            raise ValidationException(self.errors)

        return data

    def get_data(self):
        self.errors = []

        data = {}
        attrs = self.__class__._get_attributes()

        for name, schema in attrs.items():
            self._validate_attribute(name, schema, data)

        return data

    @classmethod
    def get_boolean_from_checkbox(cls, name, value, form_data):
        return value == 'on'

    def _assert_required(self, name, value, schema):
        error_message = 'The field {} is required.'

        if self._is_falsy(value) and schema.get(self.required_str):
            self.errors.append(error_message.format(name))

    def _assert_type(self, name, value, schema):
        error_message = 'The field {} is not of type {}.'

        value_type = schema.get(self.type_str)
        default = schema.get(self.default_str)

        if self._is_falsy(value) and self.default_str in schema:
            if default is None:
                return
            else:
                value = default

        try:
            value_type(value)
        except ValueError:
            self.errors.append(error_message.format(name, value_type.__name__))
            return

        accepted_values = self.types.get(value_type.__name__)
        if accepted_values is not None:
            if callable(accepted_values) and not accepted_values(value):
                self.errors.append(error_message.format(name, value_type.__name__))

            if type(accepted_values) is list and value not in accepted_values:
                self.errors.append(error_message.format(name, value_type.__name__))

    def _is_falsy(self, value):
        return value is None or value == ''

    def _validate_attribute(self, name, schema, data):
        value = self.form_data.get(name)
        default_value = schema.get(self.default_str)
        field_type = schema.get(self.type_str)
        get = schema.get(self.get_str)

        self._assert_required(name, value, schema)
        self._assert_type(name, value, schema)

        if get is not None and callable(get):
            data[name] = get(name, value, self.form_data)
        else:
            data[name] = (
                default_value
                if self._is_falsy(value) and self.default_str in schema
                else field_type(value)
            )

    @classmethod
    def _get_attributes(cls):
        return {
            key:value
            for key, value in cls.__dict__.items()
            if not key.startswith('__') and not callable(value)
        }


class ValidationException(BaseLtiException):
    def __init__(self, errors):
        code = 'VAL_ERRORS'
        description = '\n'.join(errors)

        BaseLtiException.__init__(self, code, description)
