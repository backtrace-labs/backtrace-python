import http.server
import json
import os
import subprocess
import sys
import unittest

tests_dir = os.path.dirname(os.path.realpath(__file__))
exe_dir = os.path.join(tests_dir, "exe")
debug_backtrace = False

def check_basic_report(obj):
    assert obj['lang'] == "python"
    assert obj['agent'] == "backtrace-python"
    assert obj['classifiers'][0] == "NameError"
    assert obj['attributes']['error.message'] == "name 'b' is not defined"

def run_one_test(check_fn, exe_name):
    requested_server_address = ("127.0.0.1", 0)

    class non_local:
        json_object = None

    class RequestHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.end_headers()
            payload = self.rfile.read()
            json_string = payload.decode('utf-8', 'strict')
            non_local.json_object = json.loads(json_string)

        def log_message(self, format, *args):
            pass

    httpd = http.server.HTTPServer(requested_server_address, RequestHandler)
    host, port = httpd.server_address

    exe_path = os.path.join(exe_dir, exe_name)
    stdio_action = None if debug_backtrace else subprocess.DEVNULL
    child = subprocess.Popen([sys.executable, exe_path, host, str(port)],
        stdout=stdio_action, stderr=stdio_action)

    httpd.handle_request()
    check_fn(non_local.json_object)
    child.wait()
    httpd.server_close()
    

class TestErrorReports(unittest.TestCase):
    def test_basic_report(self):
        run_one_test(check_basic_report, "simple_report.py")
