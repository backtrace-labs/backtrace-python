import os
import sys

from backtracepython.attributes.attribute_provider import AttributeProvider
from backtracepython.version import version_string

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class BacktraceAttributeProvider(AttributeProvider):
    def __init__(self):
        self.attributes = {
            "backtrace.agent": "backtrace-python",
            "backtrace.version": version_string,
        }

    def get(self):
        return self.attributes
