import simplejson as json
import os
import subprocess
import sys
import unittest

if sys.version_info.major >= 3:
    from http.server import HTTPServer
    from http.server import BaseHTTPRequestHandler
else:
    from BaseHTTPServer import HTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler

tests_dir = os.path.dirname(os.path.realpath(__file__))
exe_dir = os.path.join(tests_dir, "exe")
debug_backtrace = False

def check_basic_report(obj):
    assert obj['lang'] == "python"
    assert obj['agent'] == "backtrace-python"
    assert obj['classifiers'][0] == "NameError"

    if obj['langVersion'].startswith("PyPy"):
        assert obj['attributes']['error.message'] == "global name 'b' is not defined"
    else:
        assert obj['attributes']['error.message'] == "name 'b' is not defined"

    source_code_id = obj['threads'][obj['mainThread']]['stack'][0]['sourceCode']
    assert obj['sourceCode'][source_code_id]['path'].endswith("tests/exe/simple_report.py")
    assert obj['sourceCode'][source_code_id]['text'].endswith("\na = b\n")

    assert obj['attributes']['a'] == 1
    assert obj['attributes']['b'] == "bar"

def check_multi_file(obj):
    if sys.version_info.major >= 3:
        assert obj['classifiers'][0] == "JSONDecodeError"
        assert obj['attributes']['error.message'] == "Expecting value: line 1 column 1 (char 0)"
    elif obj['langVersion'].startswith("PyPy"):
        assert obj['classifiers'][0] == "ValueError"
        assert obj['attributes']['error.message'] == "Error when decoding true at char 1"
    else:
        assert obj['classifiers'][0] == "ValueError"
        assert obj['attributes']['error.message'] == "No JSON object could be decoded"

    fault_stack = obj['threads'][obj['mainThread']]['stack']
    source_code_id = fault_stack[-1]['sourceCode']
    assert obj['sourceCode'][source_code_id]['path'].endswith("tests/exe/multi_file.py")
    lines = obj['sourceCode'][source_code_id]['text'].split("\n")
    assert lines[fault_stack[-1]['line'] - 1] == 'call_a_file(True)'

    assert fault_stack[-6]['funcName'] == "bar"
    assert fault_stack[-6]['line'] == 4

def check_send_report(obj):
    if sys.version_info.major >= 3:
        assert obj['attributes']['error.message'] == "dsa"

    assert obj['attributes']['genre'] == 'happy hardcore'
    assert obj['annotations']['color'] == 'blue'

def check_threads(obj):
    if sys.version_info.major >= 3:
        assert len(obj['threads']) == 4

def run_one_test(check_fn, exe_name):
    requested_server_address = ("127.0.0.1", 0)

    class non_local:
        json_object = None

    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.end_headers()
            payload = self.rfile.read()
            json_string = payload.decode('utf-8', 'strict')
            non_local.json_object = json.loads(json_string)

        def log_message(self, format, *args):
            pass

    httpd = HTTPServer(requested_server_address, RequestHandler)
    host, port = httpd.server_address

    exe_path = os.path.join(exe_dir, exe_name)
    stdio_action = None if debug_backtrace else subprocess.PIPE
    child = subprocess.Popen([sys.executable, exe_path, host, str(port)],
        stdout=stdio_action, stderr=stdio_action)

    httpd.handle_request()
    check_fn(non_local.json_object)
    child.wait()
    if stdio_action is not None:
        child.stdout.close()
        child.stderr.close()
    httpd.server_close()
    

class TestErrorReports(unittest.TestCase):
    def test_basic_report(self):
        run_one_test(check_basic_report, "simple_report.py")

    def test_multi_file(self):
        run_one_test(check_multi_file, "multi_file.py")

    def test_send_report(self):
        run_one_test(check_send_report, "send_report.py")

    def test_threads(self):
        run_one_test(check_threads, "threads.py")
