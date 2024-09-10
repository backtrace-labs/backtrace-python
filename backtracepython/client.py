import os
import sys
import simplejson as json
import subprocess

from backtracepython.attributes.attribute_manager import attribute_manager
from backtracepython.report import BacktraceReport

if sys.version_info.major >= 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode


class globs:
    endpoint = None
    next_except_hook = None
    debug_backtrace = False
    timeout = None
    tab_width = None
    attributes = {}
    context_line_count = None
    worker = None


child_py_path = os.path.join(os.path.dirname(__file__), "child.py")

def get_attributes():
    return attribute_manager.get()

def send_worker_report(report, source_code):
    send_worker_msg({
        "id": "send",
        "report": report,
        "context_line_count": globs.context_line_count,
        "timeout": globs.timeout,
        "endpoint": globs.endpoint,
        "tab_width": globs.tab_width,
        "debug_backtrace": globs.debug_backtrace,
        "source_code": source_code,
    })
    

def send_worker_msg(msg):
    payload = json.dumps(msg, ignore_nan=True).encode("utf-8")
    globs.worker.stdin.write(payload)
    globs.worker.stdin.write("\n".encode("utf-8"))
    globs.worker.stdin.flush()


def create_and_send_report(ex_type, ex_value, ex_traceback):
    report = BacktraceReport()
    report.set_exception(ex_type, ex_value, ex_traceback)
    report.set_attribute("error.type", "Unhandled exception")
    report.send()




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
    globs.timeout = kwargs.get("timeout", 4)
    globs.tab_width = kwargs.get("tab_width", 8)
    globs.context_line_count = kwargs.get("context_line_count", 200)

    attribute_manager.add(kwargs.get("attributes", {}))
    stdio_value = None if globs.debug_backtrace else subprocess.PIPE
    globs.worker = subprocess.Popen(
        [sys.executable, child_py_path],
        stdin=subprocess.PIPE,
        stdout=stdio_value,
        stderr=stdio_value,
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
    send_worker_msg({"id": "terminate"})
    if not globs.debug_backtrace:
        globs.worker.stdout.close()
        globs.worker.stderr.close()
    globs.worker.wait()


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
