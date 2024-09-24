from backtracepython.client import get_attributes, set_attribute, set_attributes
from backtracepython.report import BacktraceReport


def test_setting_client_attribute():
    key = "foo"
    value = "bar"
    set_attribute(key, value)

    client_attributes = get_attributes()
    assert client_attributes[key] == value


def test_overriding_client_attribute():
    current_attributes = get_attributes()
    key = list(current_attributes.keys())[0]
    previous_value = list(current_attributes.values())[0]

    new_value = "bar"
    set_attribute(key, new_value)

    client_attributes = get_attributes()
    assert client_attributes[key] == new_value
    assert new_value != previous_value


def test_primitive_values_in_attributes():
    primitive_attributes = {
        "string": "test",
        "int": 123,
        "float": 123123.123,
        "boolean": False,
        "None": None,
    }

    set_attributes(primitive_attributes)
    new_report = BacktraceReport()
    report_attributes = new_report.get_attributes()

    for primitive_value_key in primitive_attributes:
        assert primitive_value_key in report_attributes
        assert (
            report_attributes[primitive_value_key]
            == primitive_attributes[primitive_value_key]
        )


def test_complex_objects_in_annotations():
    objects_to_test = (
        {"foo": 1, "bar": 2},
        ("foo", "bar", "baz"),
        lambda: None,
        BacktraceReport(),
    )

    for index, value in enumerate(objects_to_test):
        set_attribute(index, value)

    new_report = BacktraceReport()
    report_annotations = new_report.get_annotations()

    assert len(report_annotations) == len(objects_to_test)
