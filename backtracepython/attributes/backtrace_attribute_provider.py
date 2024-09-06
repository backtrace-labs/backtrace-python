from backtracepython.attributes.attribute_provider import AttributeProvider
from backtracepython.version import version_string


class BacktraceAttributeProvider(AttributeProvider):
    def __init__(self):
        self.attributes = {
            "backtrace.agent": "backtrace-python",
            "backtrace.version": version_string,
        }

    def get(self):
        return self.attributes
