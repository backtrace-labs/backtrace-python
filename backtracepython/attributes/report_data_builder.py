import sys

class ReportDataBuilder:
     
    primitive_types = (int, float, bool, type(None), str) if sys.version_info.major >= 3 else (int, float, bool, type(None), str, unicode)

    @staticmethod
    def get(provider_attributes):
        attributes = {}
        annotations = {}

        # Iterate through input_dict and split based on value types
        for key, value in provider_attributes.items():
            if isinstance(value, ReportDataBuilder.primitive_types):
                attributes[key] = value
            else:
                print("Adding {} as an annotation. Type {}".format(key, type(value)))
                annotations[key] = value

        # Return both dictionaries
        return attributes, annotations
