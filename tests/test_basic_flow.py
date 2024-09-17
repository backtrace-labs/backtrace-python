import os
import subprocess
import sys
from cgi import FieldStorage

import simplejson as json

if sys.version_info.major >= 3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

tests_dir = os.path.dirname(os.path.realpath(__file__))
exe_dir = os.path.join(tests_dir, "exe")
debug_backtrace = False


def check_basic_report(obj):
    assert obj["lang"] == "python"
    assert obj["agent"] == "backtrace-python"
    assert obj["classifiers"][0] == "NameError"

    if obj["langVersion"].startswith("PyPy"):
        assert obj["attributes"]["error.message"] == "global name 'b' is not defined"
    else:
        assert obj["attributes"]["error.message"] == "name 'b' is not defined"

    source_code_id = obj["threads"][obj["mainThread"]]["stack"][0]["sourceCode"]
    assert obj["sourceCode"][source_code_id]["path"].endswith(
        os.path.join(tests_dir, "exe", "simple_report.py")
    )
    assert obj["sourceCode"][source_code_id]["text"].endswith("\na = b\n")

    assert obj["attributes"]["a"] == 1
    assert obj["attributes"]["b"] == "bar"


def check_multi_file(obj):
    if obj["langVersion"].startswith("PyPy"):
        assert obj["classifiers"][0] == "ValueError"
        assert (
            obj["attributes"]["error.message"] == "Error when decoding true at char 1"
        )
    else:
        assert obj["classifiers"][0] == "JSONDecodeError"
        assert (
            obj["attributes"]["error.message"]
            == "Expecting value: line 1 column 1 (char 0)"
        )

    fault_stack = obj["threads"][obj["mainThread"]]["stack"]
    source_code_id = fault_stack[-1]["sourceCode"]
    assert obj["sourceCode"][source_code_id]["path"].endswith(
        os.path.join(tests_dir, "exe", "multi_file.py")
    )
    lines = obj["sourceCode"][source_code_id]["text"].split("\n")
    assert lines[fault_stack[-1]["line"] - 1] == "call_a_file(True)"

    assert fault_stack[-6]["funcName"] == "bar"
    assert fault_stack[-6]["line"] == 5


def check_send_report(obj):
    if sys.version_info.major >= 3:
        assert obj["attributes"]["error.message"] == "dsa"

    assert obj["attributes"]["genre"] == "happy hardcore"
    assert obj["annotations"]["color"] == "blue"


def check_threads(obj):
    if sys.version_info.major >= 3:
        assert len(obj["threads"]) == 5


def run_one_test(check_fn, exe_name):
    requested_server_address = ("127.0.0.1", 0)

    class non_local:
        json_object = None

    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.end_headers()
            form = FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"},
            )

            payload = form["upload_file"].file.read()
            json_string = payload.decode("utf-8", "strict")
            non_local.json_object = json.loads(json_string)

        def log_message(self, format, *args):
            pass

    httpd = HTTPServer(requested_server_address, RequestHandler)
    host, port = httpd.server_address

    exe_path = os.path.join(exe_dir, exe_name)
    child = subprocess.Popen([sys.executable, exe_path, host, str(port)])

    httpd.handle_request()
    check_fn(non_local.json_object)
    child.wait()
    httpd.server_close()


def test_basic_report():
    run_one_test(check_basic_report, "simple_report.py")


def test_multi_file():
    run_one_test(check_multi_file, "multi_file.py")


def test_send_report():
    run_one_test(check_send_report, "send_report.py")


def test_threads():
    run_one_test(check_threads, "threads.py")
