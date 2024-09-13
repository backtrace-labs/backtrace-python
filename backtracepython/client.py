import sys

from backtracepython.attributes.attribute_manager import attribute_manager

from .report import BacktraceReport
from .report_queue import ReportQueue
from .request_handler import BacktraceRequestHandler
from .source_code_handler import SourceCodeHandler

if sys.version_info.major >= 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode


class globs:
    endpoint = None
    next_except_hook = None
    debug_backtrace = False
    worker = None
    attachments = []
    handler = None


def get_attributes():
    return attribute_manager.get()


def send(report, attachments=[]):
    if globs.handler is None:
        return False

    globs.handler.add(
        report.get_data(), report.get_attachments() + globs.attachments + attachments
    )
    return True


def create_and_send_report(ex_type, ex_value, ex_traceback):
    report = BacktraceReport()
    report.set_exception(ex_type, ex_value, ex_traceback)
    report.set_attribute("error.type", "Unhandled exception")
    globs.handler.process(report.get_data(), globs.attachments)


def bt_except_hook(ex_type, ex_value, ex_traceback):
    if globs.debug_backtrace:
        # Go back to normal exceptions while we do our work here.
        sys.excepthook = globs.next_except_hook

        # Now if this fails we'll get a normal exception.
        create_and_send_report(ex_type, ex_value, ex_traceback)

        # Put our exception handler back in place, and then also
        # pass the exception down the chain.
        sys.excepthook = bt_except_hook
    else:
        # Failure here is silent.
        try:
            create_and_send_report(ex_type, ex_value, ex_traceback)
        except:
            pass

    # Send the exception on to the next thing in the chain.
    globs.next_except_hook(ex_type, ex_value, ex_traceback)


def initialize(**kwargs):
    globs.endpoint = construct_submission_url(
        kwargs["endpoint"], kwargs.get("token", None)
    )
    globs.debug_backtrace = kwargs.get("debug_backtrace", False)
    globs.attachments = kwargs.get("attachments", [])
    attribute_manager.add(kwargs.get("attributes", {}))

    globs.handler = ReportQueue(
        BacktraceRequestHandler(
            globs.endpoint,
            kwargs.get("timeout", 4),
            kwargs.get("ignore_ssl_certificate", False),
            globs.debug_backtrace,
        ),
        SourceCodeHandler(
            kwargs.get("tab_width", 8), kwargs.get("context_line_count", 200)
        ),
    )

    disable_global_handler = kwargs.get("disable_global_handler", False)
    if not disable_global_handler:
        globs.next_except_hook = sys.excepthook
        sys.excepthook = bt_except_hook


def construct_submission_url(endpoint, token):
    if "submit.backtrace.io" in endpoint or token is None:
        return endpoint

    return "{}/post?{}".format(
        endpoint,
        urlencode(
            {
                "token": token,
                "format": "json",
            }
        ),
    )


def finalize():
    if globs.handler is None:
        return
    globs.handler.dispose()


def send_last_exception(**kwargs):
    report = BacktraceReport()
    report.capture_last_exception()
    report.set_dict_attributes(kwargs.get("attributes", {}))
    report.set_dict_annotations(kwargs.get("annotations", {}))
    report.set_attribute("error.type", "Exception")
    report.send()


def make_an_exception():
    try:
        raise Exception
    except:
        return sys.exc_info()


def send_report(msg, **kwargs):
    report = BacktraceReport()
    report.set_exception(*make_an_exception())
    report.set_dict_attributes(kwargs.get("attributes", {}))
    report.set_dict_annotations(kwargs.get("annotations", {}))
    report.set_attribute("error.message", msg)
    report.set_attribute("error.type", "Message")
    report.send()
