import sys


class ReportDataBuilder:

    # unicode is not available in Python3. However due to the Python2 support
    # We need to use it to verify primitive values.
    primitive_types = (
        (int, float, bool, type(None), str)
        if sys.version_info.major >= 3
        else (int, float, bool, type(None), str, unicode)
    )

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
