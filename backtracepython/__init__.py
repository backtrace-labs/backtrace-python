from __future__ import print_function
import json
import math
import os
import platform
import socket
import sys
import threading
import time
import uuid

if sys.version_info.major >= 3:
    from urllib.parse import urlencode
    from urllib.request import Request
    from urllib.request import urlopen
else:
    from urllib import urlencode
    from urllib2 import urlopen
    from urllib2 import Request

__all__ = ["BacktraceReport", "initialize", "version", "version_string"]

class version:
    major = 0
    minor = 0
    patch = 0

version_string = "{}.{}.{}".format(version.major, version.minor, version.patch)

class globs:
    endpoint = None
    token = None
    next_except_hook = None
    debug_backtrace = False
    timeout = None
    tab_width = None
    attributes = None
    context_line_count = None
    next_source_code_id = 0

process_start_time = time.time()

def get_process_age():
    return int(time.time() - process_start_time)

def get_python_version():
    return "{} {}.{}.{}-{}".format(
        platform.python_implementation(),
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
        sys.version_info.releaselevel)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def post_json(endpoint, path, query, obj):
    if globs.debug_backtrace:
        eprint(json.dumps(obj, indent=2))
    payload = json.dumps(obj).encode('utf-8')
    query = urlencode(query)
    headers = {
        'Content-Type': "application/json",
        'Content-Length': len(payload),
    }
    full_url = "{}/post?{}".format(globs.endpoint, query)
    req = Request(full_url, payload, headers)
    with urlopen(req) as resp:
        if resp.code != 200:
            raise Exception(resp.code, resp.read())

def walk_tb_backwards(tb):
    while tb is not None:
        yield tb.tb_frame, tb.tb_lineno
        tb = tb.tb_next

def walk_tb(tb):
    return reversed(list(walk_tb_backwards(tb)))

def make_unique_source_code_id():
    result = str(globs.next_source_code_id)
    globs.next_source_code_id += 1
    return result

def read_file_or_none(file_path):
    try:
        with open(file_path) as f:
            return f.read()
    except:
        return None

def create_source_object(source_path):
    ext = os.path.splitext(source_path)[1]
    if ext == ".py":
        text = read_file_or_none(source_path)
        if text is not None:
            return {
                'text': text,
                'startLine': 1,
                'startColumn': 1,
                'startPos': 0,
                'path': source_path,
                'tabWidth': globs.tab_width,
            }
    return { 'path': source_path }

def add_source_code(source_path, source_code_dict, source_path_dict):
    try:
        return source_path_dict[source_path]
    except KeyError:
        the_id = make_unique_source_code_id()
        source_path_dict[source_path] = the_id
        source_code_dict[the_id] = create_source_object(source_path)
        return the_id

def process_frame(tb_frame, line, source_code_dict, source_path_dict):
    source_file = os.path.abspath(tb_frame.f_code.co_filename)
    frame = {
        'funcName': tb_frame.f_code.co_name,
        'line': line,
        'sourceCode': add_source_code(source_file, source_code_dict, source_path_dict),
    }
    return frame

def get_main_thread():
    if sys.version_info.major >= 3:
        return threading.main_thread()
    first = None
    for thread in threading.enumerate():
        if thread.name == 'MainThread':
            return thread
        if first is None:
            first = thread
    return first

class BacktraceReport:
    def __init__(self):
        self.fault_thread = threading.current_thread()
        self.source_code = {}
        self.source_path_dict = {}

        import __main__
        entry_path = os.path.abspath(__main__.__file__)
        cwd_path = os.path.abspath(os.getcwd())
        entry_thread = get_main_thread()
        entry_source_code_id = add_source_code(entry_path, self.source_code, self.source_path_dict)

        init_attrs = {
            'hostname': socket.gethostname(),
            'process.age': get_process_age(),
        }
        init_attrs.update(globs.attributes)

        self.log_lines = []

        self.report = {
            'uuid': str(uuid.uuid4()),
            'timestamp': int(time.time()),
            'lang': "python",
            'langVersion': get_python_version(),
            'agent': "backtrace-python",
            'agentVersion': version_string,
            'mainThread': str(self.fault_thread.ident),
            'entryThread': str(entry_thread.ident),
            'entrySourceCode': entry_source_code_id,
            'cwd': cwd_path,
            'attributes': init_attrs,
            'sourceCode': self.source_code,
            'annotations': {
                'Environment Variables': dict(os.environ),
            },
        }

    def set_exception(self, garbage, ex_value, ex_traceback):
        self.report['classifiers'] = [ex_value.__class__.__name__]
        self.report['attributes']['error.message'] = "\n".join(ex_value.args)

        threads = {}
        for thread in threading.enumerate():
            if thread.ident == self.fault_thread.ident:
                threads[str(self.fault_thread.ident)] = {
                    'name': self.fault_thread.name,
                    'stack': [process_frame(frame, line, self.source_code,
                        self.source_path_dict) for frame, line in walk_tb(ex_traceback)],
                }
            else:
                threads[str(thread.ident)] = {
                    'name': thread.name,
                }

        self.report['threads'] = threads

    def capture_last_exception(self):
        self.set_exception(*sys.exc_info())

    def set_attribute(self, key, value):
        self.report['attributes'][key] = value

    def set_dict_attributes(self, target_dict):
        self.report['attributes'].update(target_dict)

    def set_annotation(self, key, value):
        self.report['annotations'][key] = value

    def log(self, line):
        self.log_lines.append({
            'ts': time.time(),
            'msg': line,
        })

    def send(self):
        if len(self.log_lines) != 0 and 'Log' not in self.report['annotations']:
            self.report['annotations']['Log'] = self.log_lines
        query = {
            'token': globs.token,
            'format': "json",
        }
        post_json(globs.endpoint, "/post", query, self.report)

def create_and_send_report(ex_type, ex_value, ex_traceback):
    report = BacktraceReport()
    report.set_exception(ex_type, ex_value, ex_traceback)
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
    globs.endpoint = kwargs['endpoint']
    globs.token = kwargs['token']
    globs.debug_backtrace = kwargs.get('debug_backtrace', False)
    globs.timeout = kwargs.get('timeout', 4)
    globs.tab_width = kwargs.get('tab_width', 8)
    globs.attributes = kwargs.get('attributes', {})
    globs.context_line_count = kwargs.get('context_line_count', 200)
    disable_global_handler = kwargs.get('disable_global_handler', False)
    if not disable_global_handler:
        globs.next_except_hook = sys.excepthook
        sys.excepthook = bt_except_hook
