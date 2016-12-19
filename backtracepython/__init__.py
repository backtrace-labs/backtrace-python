import json
import math
import os
import platform
import socket
import subprocess
import sys
import threading
import time
import uuid

__all__ = ["BacktraceReport", "initialize", "finalize", "terminate", "version", "version_string", "send_last_exception", "send_report"]

class version:
    major = 0
    minor = 3
    patch = 1

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
    worker = None
    next_source_code_id = 0

process_start_time = time.time()
child_py_path = os.path.join(os.path.dirname(__file__), "child.py")

def get_process_age():
    return int(time.time() - process_start_time)

def get_python_version():
    return "{} {}.{}.{}-{}".format(
        platform.python_implementation(),
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
        sys.version_info.releaselevel)

def send_worker_msg(msg):
    payload = json.dumps(msg).encode('utf-8')
    globs.worker.stdin.write(payload)
    globs.worker.stdin.write("\n".encode('utf-8'))
    globs.worker.stdin.flush()

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

def add_source_code(source_path, source_code_dict, source_path_dict, line):
    try:
        the_id = source_path_dict[source_path]
    except KeyError:
        the_id = make_unique_source_code_id()
        source_path_dict[source_path] = the_id
        source_code_dict[the_id] = {
            'minLine': line,
            'maxLine': line,
            'path': source_path,
        }
        return the_id

    if line < source_code_dict[the_id]['minLine']:
        source_code_dict[the_id]['minLine'] = line
    if line > source_code_dict[the_id]['maxLine']:
        source_code_dict[the_id]['maxLine'] = line
    return the_id

def process_frame(tb_frame, line, source_code_dict, source_path_dict):
    source_file = os.path.abspath(tb_frame.f_code.co_filename)
    frame = {
        'funcName': tb_frame.f_code.co_name,
        'line': line,
        'sourceCode': add_source_code(source_file, source_code_dict, source_path_dict, line),
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
        entry_source_code_id = add_source_code(entry_path, self.source_code, self.source_path_dict, 1)

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

    def set_dict_annotations(self, target_dict):
        self.report['annotations'].update(target_dict)

    def log(self, line):
        self.log_lines.append({
            'ts': time.time(),
            'msg': line,
        })

    def send(self):
        if len(self.log_lines) != 0 and 'Log' not in self.report['annotations']:
            self.report['annotations']['Log'] = self.log_lines
        send_worker_msg({
            'id': 'send',
            'report': self.report,
            'context_line_count': globs.context_line_count,
            'timeout': globs.timeout,
            'token': globs.token,
            'endpoint': globs.endpoint,
            'tab_width': globs.tab_width,
            'debug_backtrace': globs.debug_backtrace,
            'source_code': self.source_code,
        })

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

    stdio_value = None if globs.debug_backtrace else subprocess.PIPE
    globs.worker = subprocess.Popen([sys.executable, child_py_path],
        stdin=subprocess.PIPE, stdout=stdio_value, stderr=stdio_value)

    disable_global_handler = kwargs.get('disable_global_handler', False)
    if not disable_global_handler:
        globs.next_except_hook = sys.excepthook
        sys.excepthook = bt_except_hook

def finalize():
    send_worker_msg({ 'id': 'terminate' })
    if not globs.debug_backtrace:
        globs.worker.stdout.close()
        globs.worker.stderr.close()
    globs.worker.wait()

def send_last_exception(**kwargs):
    report = BacktraceReport()
    report.capture_last_exception()
    report.set_dict_attributes(kwargs.get('attributes', {}))
    report.set_dict_annotations(kwargs.get('annotations', {}))
    report.send()


def make_an_exception():
    try:
        raise Exception
    except:
        return sys.exc_info()

def send_report(msg, **kwargs):
    report = BacktraceReport()
    report.set_exception(*make_an_exception())
    report.set_dict_attributes(kwargs.get('attributes', {}))
    report.set_dict_annotations(kwargs.get('annotations', {}))
    report.report['attributes']['error.message'] = msg
    report.send()
