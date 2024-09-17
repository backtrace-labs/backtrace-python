import os
import sys
import threading
import time
import uuid

from backtracepython.attributes.attribute_manager import attribute_manager

from .utils import python_version
from .version import version_string


class BacktraceReport:
    def __init__(self):
        self.fault_thread = threading.current_thread()
        self.source_code = {}
        self.source_path_dict = {}
        self.attachments = []

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
            "attributes": init_attrs,
            "annotations": {
                "Environment Variables": dict(os.environ),
            },
            "threads": self.generate_stack_trace(),
        }

    def set_exception(self, garbage, ex_value, ex_traceback):
        self.report["classifiers"] = [ex_value.__class__.__name__]
        self.report["attributes"]["error.message"] = str(ex_value)

        # update faulting thread with information from the error
        fault_thread_id = str(self.fault_thread.ident)
        if not fault_thread_id in self.report["threads"]:
            self.report["threads"][fault_thread_id] = {
                "name": self.fault_thread.name,
                "stack": [],
                "fault": True,
            }

        faulting_thread = self.report["threads"][fault_thread_id]

        faulting_thread["stack"] = self.convert_stack_trace(
            self.traverse_exception_stack(ex_traceback), False
        )
        faulting_thread["fault"] = True

    def generate_stack_trace(self):
        current_frames = sys._current_frames()
        threads = {}
        for thread in threading.enumerate():
            thread_frame = current_frames.get(thread.ident)
            is_main_thread = thread.name == "MainThread"
            threads[str(thread.ident)] = {
                "name": thread.name,
                "stack": self.convert_stack_trace(
                    self.traverse_process_thread_stack(thread_frame), is_main_thread
                ),
                "fault": is_main_thread,
            }

        return threads

    def traverse_exception_stack(self, traceback):
        stack = []
        while traceback:
            stack.append({"frame": traceback.tb_frame, "line": traceback.tb_lineno})
            traceback = traceback.tb_next
        return reversed(stack)

    def traverse_process_thread_stack(self, thread_frame):
        stack = []
        while thread_frame:
            stack.append({"frame": thread_frame, "line": thread_frame.f_lineno})
            thread_frame = thread_frame.f_back
        return stack

    def convert_stack_trace(self, thread_stack_trace, skip_backtrace_module):
        stack_trace = []

        for thread_stack_frame in thread_stack_trace:
            # do not generate frames from our modules when we're reporting messages
            thread_frame = thread_stack_frame["frame"]
            if skip_backtrace_module:
                module = thread_frame.f_globals.get("__name__")

                if module is not None and module.startswith("backtracepython"):
                    continue

            source_file = os.path.abspath(thread_frame.f_code.co_filename)

            stack_trace.append(
                {
                    "funcName": thread_frame.f_code.co_name,
                    "line": thread_frame.f_lineno,
                    "library": source_file,
                    "sourceCode": source_file,
                }
            )

        return stack_trace

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

    def add_attachment(self, attachment_path):
        self.attachments.append(attachment_path)

    def get_attachments(self):
        return self.attachments

    def get_data(self):
        return self.report

    def send(self):
        if len(self.log_lines) != 0 and "Log" not in self.report["annotations"]:
            self.report["annotations"]["Log"] = self.log_lines
        from backtracepython.client import send

        send(self)
