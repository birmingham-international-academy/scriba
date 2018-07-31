class Document:
    """Represents a document with raw text and processed entities.

    Args:
        text (string): The raw text.
        data (dict, optional): The processed data.
    """

    def __init__(self, text, data=None):
        if data is None:
            data = {}

        self.text = text
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    def __eq__(self, other):
        return self.text == other.text and self.data == other.data

    def get(self, key, d=None):
        """Get the document entity given its key.

        Args:
            key (str): The key for the document entity.
            d (any, optional): Defaults to None. The default value

        Returns:
            any: The data value.
        """

        return self.data.get(key, d)

    def put(self, key, data):
        """Add a key-data mapping to the document.

        Args:
            key (str): The key associated with the value.
            data (any): The value.
        """

        self.data[key] = data
