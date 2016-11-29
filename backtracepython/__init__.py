from __future__ import print_function
import json
import math
import socket
import sys
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
    return int(time.time() - process_start_time)

class BacktraceReport:
    def __init__(self):
        pass

def get_python_version():
    return "{}.{}.{}-{}".format(
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

def create_and_send_report(ex_value, ex_traceback):
    report = {
        'uuid': str(uuid.uuid4()),
        'timestamp': int(time.time()),
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
    query = {
        'token': globs.token,
        'format': "json",
    }
    post_json(globs.endpoint, "/post", query, report)

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
