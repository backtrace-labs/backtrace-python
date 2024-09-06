from backtracepython.attributes.backtrace_attribute_provider import \
    BacktraceAttributeProvider
from backtracepython.attributes.linux_memory_attribute_provider import LinuxMemoryAttributeProvider
from backtracepython.attributes.machineId_attribute_provider import \
    MachineIdAttributeProvider
from backtracepython.attributes.process_attribute_provider import \
    ProcessAttributeProvider
from backtracepython.attributes.session_attribute_provider import \
    SessionAttributeProvider
from backtracepython.attributes.system_attribute_provider import \
    SystemAttributeProvider


class AttributeManager:

    def __init__(self):
        self.dynamic_attributes = [ProcessAttributeProvider(), LinuxMemoryAttributeProvider()]
        self.scoped_attributes = {}

        for scoped_attribute_provider in [MachineIdAttributeProvider(), BacktraceAttributeProvider(), SystemAttributeProvider(), SessionAttributeProvider()]:
            self.scoped_attributes.update(scoped_attribute_provider.get())

    def get(self):
        result = {}
        for dynamic_attribute_provider in self.dynamic_attributes:
            try:
                result.update(dynamic_attribute_provider.get())
            except:
                continue
        result.update(self.scoped_attributes)

        return result


    def add(self, attributes): 
        self.scoped_attributes.update(attributes)
        
        