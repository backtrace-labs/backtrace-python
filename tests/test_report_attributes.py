from backtracepython.client import set_attribute
from backtracepython.report import BacktraceReport

report = BacktraceReport()


def test_report_session_attribute_is_defined():
    assert report.get_attributes()["application.session"] is not None


def test_report_session_attribute_doesnt_change():
    compare_report = BacktraceReport()

    assert (
        report.get_attributes()["application.session"]
        == compare_report.get_attributes()["application.session"]
    )


def test_report_backtrace_reporter_attributes():
    attributes = report.get_attributes()
    assert attributes["backtrace.agent"] == "backtrace-python"
    assert attributes["backtrace.version"] is not None


def test_report_attribute_override():
    override_report = BacktraceReport()
    expected_value = "test"
    # attribute name that is defined
    override_attribute_name = "hostname"
    override_report.set_attribute(override_attribute_name, expected_value)

    assert override_report.get_attributes()[override_attribute_name] == expected_value


def test_unique_user_id():
    attributes = report.get_attributes()
    assert attributes["guid"] is not None


def test_unique_user_should_always_be_the_same():
    override_report = BacktraceReport()
    attributes = report.get_attributes()
    override_report_attributes = override_report.get_attributes()
    assert attributes["guid"] == override_report_attributes["guid"]


def test_override_default_client_attribute():
    test_attribute = "guid"
    test_attribute_value = "foo"
    set_attribute(test_attribute, test_attribute_value)
    new_report = BacktraceReport()
    attributes = new_report.get_attributes()
    assert attributes["guid"] == test_attribute_value


def test_override_default_client_attribute_by_report():
    test_attribute = "guid"
    test_attribute_value = "bar"
    new_report = BacktraceReport()
    new_report.set_attribute(test_attribute, test_attribute_value)
    attributes = new_report.get_attributes()
    assert attributes["guid"] == test_attribute_value
