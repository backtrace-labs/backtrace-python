import json
import math
import socket
import sys
import time
import urllib.parse
import urllib.request
import uuid

__all__ = ["BacktraceReport", "initialize", "version", "version_string"]

class globs:
    endpoint = None
    token = None
    next_except_hook = None
    debug_backtrace = False
    timeout = None

class version:
    major = 0
    minor = 0
    patch = 0

version_string = "{}.{}.{}".format(version.major, version.minor, version.patch)
process_start_time = time.time()

def get_process_age():
    return math.floor(time.time() - process_start_time)

class BacktraceReport:
    def __init__(self):
        pass

def get_python_version():
    return "{}.{}.{}-{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
        sys.version_info.releaselevel)

def create_and_send_report(ex_value, ex_traceback):
    report = {
        'uuid': str(uuid.uuid4()),
        'timestamp': math.floor(time.time()),
        'lang': "python",
        'langVersion': get_python_version(),
        'agent': "backtrace-python",
        'agentVersion': version_string,
        'classifiers': [ex_value.__class__.__name__],
        'attributes': {
            'hostname': socket.gethostname(),
            'process.age': get_process_age(),
            'error.message': "\n".join(ex_value.args),
        },
    }
    payload = json.dumps(report).encode('utf-8')
    query = urllib.parse.urlencode({
        'token': globs.token,
        'format': "json",
    })
    headers = {
        'Content-Type': "application/json",
        'Content-Length': len(payload),
    }
    full_url = "{}/post?{}".format(globs.endpoint, query)
    req = urllib.request.Request(full_url, payload, headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        if resp.code != 200:
            raise Exception(resp.code, resp.read())

def bt_except_hook(ex_type, ex_value, ex_traceback):
    if globs.debug_backtrace:
        # Go back to normal exceptions while we do our work here.
        sys.excepthook = globs.next_except_hook

        # Now if this fails we'll get a normal exception.
        create_and_send_report(ex_value, ex_traceback)

        # Put our exception handler back in place, and then also
        # pass the exception down the chain.
        sys.excepthook = bt_except_hook
    else:
        # Failure here is silent.
        try:
            create_and_send_report(ex_value, ex_traceback)
        except:
            pass

    # Send the exception on to the next thing in the chain.
    globs.next_except_hook(ex_type, ex_value, ex_traceback)

def initialize(**kwargs):
    globs.endpoint = kwargs['endpoint']
    globs.token = kwargs['token']
    globs.debug_backtrace = kwargs.get('debug_backtrace', False)
    globs.timeout = kwargs.get('timeout', 4)

    globs.next_except_hook = sys.excepthook
    sys.excepthook = bt_except_hook
