class BaseRequestForm:
    def __init__(self, form_data):
        self.form_data = form_data

    @classmethod
    def _get_attributes(cls):
        return {
            key:value
            for key, value in cls.__dict__.items()
            if not key.startswith('__') and not callable(value)
        }

    @classmethod
    def get_boolean_from_checkbox(cls, name, value, form_data):
        return name == value

    def get_data(self):
        data = {}
        attrs = self.__class__._get_attributes()

        for name, schema in attrs.items():
            value = self.form_data.get(name)
            default_value = schema.get('default')
            field_type = schema.get('type')
            get = schema.get('get')

            if value is not None:
                data[name] = default_value if value == '' else field_type(value)
            elif get is not None and callable(get):
                data[name] = get(name, value, self.form_data)

        return data

    def is_valid(self):
        raise NotImplementedError()
