import platform

from backtracepython.attributes.attribute_provider import AttributeProvider


class SystemAttributeProvider(AttributeProvider):
    def __init__(self):
        self.attributes = {
            'uname.sysname': platform.system(),
            'uname.version': platform.version(),
            'uname.release': platform.release()
        }

    def get(self):
        return self.attributes
