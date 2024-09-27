from backtracepython.attributes.attribute_provider import AttributeProvider
from backtracepython.version import version_string


class UserAttributeProvider(AttributeProvider):
    def __init__(self, attributes):
        self.attributes = attributes

    def get(self):
        return self.attributes
