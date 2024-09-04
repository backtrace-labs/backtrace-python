from backtracepython import BacktraceReport

report = BacktraceReport()

def test_report_session_attribute_is_defined():
    assert report.get_attributes()['application.session'] is not None

def test_report_session_attribute_doesnt_change():
    compare_report = BacktraceReport()

    assert report.get_attributes()['application.session'] == compare_report.get_attributes()['application.session']

def test_report_backtrace_reporter_attributes():
    attributes = report.get_attributes()
    assert attributes['backtrace.agent'] == 'backtrace-python'
    assert attributes['backtrace.version'] is not None

def test_report_attribute_override():
    override_report = BacktraceReport()
    expected_value = "test"
    # attribute name that is defined
    override_attribute_name = "hostname"
    override_report.set_attribute(override_attribute_name, expected_value)

    assert override_report.get_attributes()[override_attribute_name] == expected_value