import os
import sys
import threading
import time
import uuid

from backtracepython.attributes.attribute_manager import attribute_manager
from backtracepython.utils import python_version
from backtracepython.version import version_string


def add_source_code(source_path, source_code_dict, source_path_dict, line):
    try:
        the_id = source_path_dict[source_path]
    except KeyError:
        the_id = str(uuid.uuid4())
        source_path_dict[source_path] = the_id
        source_code_dict[the_id] = {
            "minLine": line,
            "maxLine": line,
            "path": source_path,
        }
        return the_id

    if line < source_code_dict[the_id]["minLine"]:
        source_code_dict[the_id]["minLine"] = line
    if line > source_code_dict[the_id]["maxLine"]:
        source_code_dict[the_id]["maxLine"] = line
    return the_id


def process_frame(tb_frame, line, source_code_dict, source_path_dict):
    source_file = os.path.abspath(tb_frame.f_code.co_filename)
    frame = {
        "funcName": tb_frame.f_code.co_name,
        "line": line,
        "sourceCode": add_source_code(
            source_file, source_code_dict, source_path_dict, line
        ),
    }
    return frame


def get_main_thread():
    if sys.version_info.major >= 3:
        return threading.main_thread()
    first = None
    for thread in threading.enumerate():
        if thread.name == "MainThread":
            return thread
        if first is None:
            first = thread
    return first


def walk_tb_backwards(tb):
    while tb is not None:
        yield tb.tb_frame, tb.tb_lineno
        tb = tb.tb_next


def walk_tb(tb):
    return reversed(list(walk_tb_backwards(tb)))


class BacktraceReport:
    def __init__(self):
        self.fault_thread = threading.current_thread()
        self.source_code = {}
        self.source_path_dict = {}
        entry_source_code_id = None
        import __main__

        cwd_path = os.path.abspath(os.getcwd())
        entry_thread = get_main_thread()
        if hasattr(__main__, "__file__"):
            entry_source_code_id = (
                add_source_code(
                    __main__.__file__, self.source_code, self.source_path_dict, 1
                )
                if hasattr(__main__, "__file__")
                else None
            )

        init_attrs = {"error.type": "Exception"}
        init_attrs.update(attribute_manager.get())

        self.log_lines = []

        self.report = {
            "uuid": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "lang": "python",
            "langVersion": python_version,
            "agent": "backtrace-python",
            "agentVersion": version_string,
            "mainThread": str(self.fault_thread.ident),
            "entryThread": str(entry_thread.ident),
            "cwd": cwd_path,
            "attributes": init_attrs,
            "annotations": {
                "Environment Variables": dict(os.environ),
            },
        }
        if entry_source_code_id is not None:
            self.report["entrySourceCode"] = entry_source_code_id

    def set_exception(self, garbage, ex_value, ex_traceback):
        self.report["classifiers"] = [ex_value.__class__.__name__]
        self.report["attributes"]["error.message"] = str(ex_value)

        threads = {}
        for thread in threading.enumerate():
            if thread.ident == self.fault_thread.ident:
                threads[str(self.fault_thread.ident)] = {
                    "name": self.fault_thread.name,
                    "stack": [
                        process_frame(
                            frame, line, self.source_code, self.source_path_dict
                        )
                        for frame, line in walk_tb(ex_traceback)
                    ],
                }
            else:
                threads[str(thread.ident)] = {
                    "name": thread.name,
                }

        self.report["threads"] = threads

    def capture_last_exception(self):
        self.set_exception(*sys.exc_info())

    def set_attribute(self, key, value):
        self.report["attributes"][key] = value

    def set_dict_attributes(self, target_dict):
        self.report["attributes"].update(target_dict)

    def set_annotation(self, key, value):
        self.report["annotations"][key] = value

    def get_attributes(self):
        return self.report["attributes"]

    def set_dict_annotations(self, target_dict):
        self.report["annotations"].update(target_dict)

    def log(self, line):
        self.log_lines.append(
            {
                "ts": time.time(),
                "msg": line,
            }
        )

    def send(self):
        if len(self.log_lines) != 0 and "Log" not in self.report["annotations"]:
            self.report["annotations"]["Log"] = self.log_lines
        from backtracepython.client import send_worker_report

        send_worker_report(self.report, self.source_code)
