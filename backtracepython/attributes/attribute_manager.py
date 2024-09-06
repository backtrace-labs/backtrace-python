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
        self.dynamic_attributes = [
            ProcessAttributeProvider(),
            LinuxMemoryAttributeProvider(),
        ]
        self.scoped_attributes = {}
        self.scoped_attribute_providers = [
            MachineIdAttributeProvider(),
            BacktraceAttributeProvider(),
            SystemAttributeProvider(),
            SessionAttributeProvider(),
            MachineAttributeProvider(),
        ]
        for scoped_attribute_provider in self.scoped_attribute_providers:
            self.safety_add(self.scoped_attributes, scoped_attribute_provider)

    def get(self):
        result = {}
        for dynamic_attribute_provider in self.dynamic_attributes:
            self.safety_add(result, dynamic_attribute_provider)
        result.update(self.scoped_attributes)

        return result

    def add(self, attributes):
        self.scoped_attributes.update(attributes)

    def safety_add(self, dictionary, provider):
        try:
            dictionary.update(provider.get())
        except:
            return
