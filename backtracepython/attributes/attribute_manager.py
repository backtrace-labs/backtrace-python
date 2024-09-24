import platform

from .backtrace_attribute_provider import BacktraceAttributeProvider
from .linux_memory_attribute_provider import LinuxMemoryAttributeProvider
from .machine_attribute_provider import MachineAttributeProvider
from .machineId_attribute_provider import MachineIdAttributeProvider
from .process_attribute_provider import ProcessAttributeProvider
from .report_data_builder import ReportDataBuilder
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

            generated_attributes, generated_annotations = ReportDataBuilder.get(
                self.try_get(attribute_provider)
            )
            attributes.update(generated_attributes)
            annotations.update(generated_annotations)

        return attributes, annotations

    def add(self, attributes):
        self.attribute_providers.append(UserAttributeProvider(attributes))

    def try_get(self, provider):
        try:
            return provider.get()
        except:
            return {}

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
