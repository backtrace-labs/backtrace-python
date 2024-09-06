import platform

from backtracepython.attributes.attribute_provider import AttributeProvider


class SystemAttributeProvider(AttributeProvider):
    def __init__(self):
        self.attributes = {
            "uname.sysname": self.getPlatformName(),
            "uname.version": platform.version(),
            "uname.release": platform.release(),
        }

    def get(self):
        return self.attributes

    def getPlatformName(self):
        sys_name = platform.system()

        if sys_name == "Darwin":
            return "Mac OS"
        return sys_name
