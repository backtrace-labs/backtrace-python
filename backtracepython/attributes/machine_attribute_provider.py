import platform
import socket

from backtracepython.attributes.attribute_provider import AttributeProvider


class MachineAttributeProvider(AttributeProvider):
    def get(self):
        return {
            "hostname": socket.gethostname(),
            "cpu.arch": platform.machine(),
            "cpu.brand": platform.processor(),
        }
