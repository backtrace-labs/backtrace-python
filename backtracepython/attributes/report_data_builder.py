import unicodedata


class ReportDataBuilder:
    primitive_types = (int, float, str, bool, bytes, type(None))

    @staticmethod
    def get(provider_attributes):
        attributes = {}
        annotations = {}

        # Iterate through input_dict and split based on value types
        for key, value in provider_attributes.items():
            if isinstance(value, ReportDataBuilder.primitive_types):
                attributes[key] = value
            else:
                annotations[key] = value

        # Return both dictionaries
        return attributes, annotations
