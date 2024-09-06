import uuid

from backtracepython.attributes.attribute_provider import AttributeProvider


class SessionAttributeProvider(AttributeProvider):
    def __init__(self):
        self.attributes = {"application.session": str(uuid.uuid4())}

    def get(self):
        return self.attributes
