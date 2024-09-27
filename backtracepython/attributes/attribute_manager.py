import platform

from .backtrace_attribute_provider import BacktraceAttributeProvider
from .linux_memory_attribute_provider import LinuxMemoryAttributeProvider
from .machine_attribute_provider import MachineAttributeProvider
from .machineId_attribute_provider import MachineIdAttributeProvider
from .process_attribute_provider import ProcessAttributeProvider
from .report_data_builder import get_report_attributes
from .session_attribute_provider import SessionAttributeProvider
from .system_attribute_provider import SystemAttributeProvider
from .user_attribute_provider import UserAttributeProvider


class AttributeManager:
    def __init__(self):
        self.attribute_providers = (
            self.get_predefined_dynamic_attribute_providers()
            + self.get_predefined_scoped_attribute_providers()
        )

    def get(self):
        attributes = {}
        annotations = {}
        for attribute_provider in self.attribute_providers:
            try:
                provider_attributes = attribute_provider.get()
                generated_attributes, generated_annotations = get_report_attributes(
                    provider_attributes
                )
                attributes.update(generated_attributes)
                annotations.update(generated_annotations)
            except:
                continue

        return attributes, annotations

    def add(self, attributes):
        self.attribute_providers.append(UserAttributeProvider(attributes))

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
