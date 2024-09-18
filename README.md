# backtrace-python

[Backtrace](http://backtrace.io/) error reporting tool for Python.

## Documentation

https://support.backtrace.io/hc/en-us/articles/360040105992-Python-Integration-Guide

## Installation

### Requirements

This module supports Python 2, Python 3, and PyPy.

```
python -m pip install backtracepython
```

## Basic Usage

```python
import backtracepython as bt
bt.initialize(
    endpoint="https://submit.backtrace.io/{universe}/{token}/json"
)
```

### Sending Reports from Unhandled Exceptions

By default, the `backtracepython` module automatically captures unhandled exceptions and creates and sends error reports from them. This behavior can be adjusted with the `disable_global_handler` option in `bt.initialize` (see below).

### Sending Reports Manually

You can also send error reports manually in your code. However, to get a correct callstack and source code context, you must send an error with a Python exception context. To do this, you can raise a Python exception and then immediately send a report using the `send_last_exception` call. Here's an example:

```python
try:
    raise Exception("This report was sent manually.")
except:
    bt.send_last_exception()
```

## Documentation

### bt.initialize

#### Arguments

- endpoint  - Required. Example: https://yourcompany.sp.backtrace.io:6098 or https://submit.backtrace.io/{universe}/{token}/json.  Sets the HTTP/HTTPS endpoint that error reports will be sent to. If submit.backtrace.io url is provided, the token argument is not required.
  token  -  Required only if endpoint is not set to submit.backtrace.io. Example: 51cc8e69c5b62fa8c72dc963e730f1e8eacbd243aeafc35d08d05ded9a024121  Sets the token that will be used for authentication when sending an error report.
- attributes  - Dictionary that contains additional attributes to be sent along with every error report. These can be overridden on an individual report with report.set_attribute  Example: { 'application': "ApplicationName", 'serverId': "foo" }. Attributes values should be set to a primitive value such as boolean, integer or string.
- attachments - A list of file paths that will be sent with each report.
- ignore_ssl_certificate - Defaults to False. If True, ssl verification will be ignored during HTTP submission.
- timeout  - Defaults to 4. Maximum amount of seconds to wait for error report processing and sending before concluding it failed.
- debug_backtrace - Defaults to False . Set to True to have an error during collecting the report raise an exception, and to print some debugging information to stderr.
- disable_global_handler - Defaults to False. If this is False  this module will insert itself in the sys.excepthook chain and report those errors automatically before re-raising the exception. Set to True  to disable this. Note that in this case the only way error reports will be reported is if you manually create and send them.
- context_line_count  - Defaults to 200 . When an error is reported, this many lines above and below each stack function are included in the report.
- tab_width  - Defaults to 8.  If there are any hard tabs in the source code, it is unclear how many spaces they should be indented to correctly display the source code. Therefore the error report can override this number to specify how many spaces a hard tab should be represented by when viewing source code.
- collect_source_code - Default to True. By default Backtrace client collects corresponded source code and send it with the report. If set to False, the source code will not be collected.

### bt.BacktraceReport

Create a report object that you can later choose whether or not to send. This may be useful to track something like a request.

`report.set_attribute(key, value) `
Adds an attribute to a specific report. Valid types for value are str, float, int, and bool.
Attributes are indexed and searchable. See also `addAnnotation`

`report.set_dict_attributes(dict)`

Adds all key-value pairs of dict into the report recursively.

`report.get_attributes() `

Returns all report attributes.

`report.set_annotation(key, value) `

Adds an annotation to a specific report. Annotations, unlike attributes, are not indexed and searchable. However, they are available for inspection when you view a specific report.

key - String which is the name of the annotation.
value - Any type which is JSON-serializable.

`report.set_dict_annotations(dict) `

Adds all key-value pairs of dict into the report.

`report.add_attachment(attachment_path) `

Adds an attachment to the report.

`report.get_attachments() `

Returns a list of attachment paths.

`report.set_exception(ExceptionType, exception, traceback)`

error  is an Error object. Backtrace will extract information from this object such as the error message and stack trace and send this information along with the report.

`report.capture_last_exception() `

This is the same as report.set_exception(\*sys.exc_info())

`report.log(line)`

Adds a timestamped log message to the report. Log output is available when you view a report.

`report.send()`

Sends the error report to the endpoint specified in initialize.

### bt.send_last_exception(\*\*kwargs)

- attributes  - dictionary of attributes to add to the report. See report.set_dict_attributes
- annotations  - dictionary of annotations to add to the report. See report.set_dict_annotations

## Contributing

To run the test suite:

```
pytest
```

Since all of these implementations of Python are supported, be sure to run the
test suite with all of them:

- Python 2
- Python 3
- PyPy

### Publishing to PyPI

1. Make sure all tests pass (see above).
2. Update version number in backtracepython module.
3. Tag the version in git.

```
python3 setup.py bdist_wheel --universal
twine upload dist/*
```
