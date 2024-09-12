import platform

from backtracepython.attributes.backtrace_attribute_provider import (
    BacktraceAttributeProvider,
)
from backtracepython.attributes.linux_memory_attribute_provider import (
    LinuxMemoryAttributeProvider,
)
from backtracepython.attributes.machine_attribute_provider import (
    MachineAttributeProvider,
)
from backtracepython.attributes.machineId_attribute_provider import (
    MachineIdAttributeProvider,
)
from backtracepython.attributes.process_attribute_provider import (
    ProcessAttributeProvider,
)
from backtracepython.attributes.session_attribute_provider import (
    SessionAttributeProvider,
)
from backtracepython.attributes.system_attribute_provider import SystemAttributeProvider


class AttributeManager:
    def __init__(self):
        self.dynamic_attributes = self.get_predefined_dynamic_attribute_providers()
        self.scoped_attributes = {}
        for (
            scoped_attribute_provider
        ) in self.get_predefined_scoped_attribute_providers():
            self.try_add(self.scoped_attributes, scoped_attribute_provider)

    def get(self):
        result = {}
        for dynamic_attribute_provider in self.dynamic_attributes:
            self.try_add(result, dynamic_attribute_provider)
        result.update(self.scoped_attributes)

        return result

    def add(self, attributes):
        self.scoped_attributes.update(attributes)

    def try_add(self, dictionary, provider):
        try:
            dictionary.update(provider.get())
        except:
            return

    def get_predefined_scoped_attribute_providers(self):
        return [
            MachineIdAttributeProvider(),
            BacktraceAttributeProvider(),
            SystemAttributeProvider(),
            SessionAttributeProvider(),
            MachineAttributeProvider(),
        ]

    def get_predefined_dynamic_attribute_providers(self):
        result = [ProcessAttributeProvider()]

        if platform.system() == "Linux":
            result.append(LinuxMemoryAttributeProvider())

        return result


attribute_manager = AttributeManager()
