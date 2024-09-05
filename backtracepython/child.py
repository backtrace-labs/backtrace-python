from __future__ import print_function

import os
import sys

import simplejson as json

if sys.version_info.major >= 3:
    from urllib.request import Request
    from urllib.request import urlopen
else:
    from urllib2 import urlopen
    from urllib2 import Request

class globs:
    tab_width = None
    debug_backtrace = None
    context_line_count = None

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def post_json(full_url, obj):
    if globs.debug_backtrace:
        eprint(full_url)
        eprint(json.dumps(obj, indent=2, ignore_nan=True))
    payload = json.dumps(obj, ignore_nan=True).encode('utf-8')
    headers = {
        'Content-Type': "application/json",
        'Content-Length': len(payload),
    }
    req = Request(full_url, payload, headers)
    resp = urlopen(req)
    if resp.code != 200:
        raise Exception(resp.code, resp.read())

def read_file_or_none(file_path):
    try:
        with open(file_path) as f:
            return f.read()
    except:
        return None

def create_source_object(source_path, min_line, max_line):
    ext = os.path.splitext(source_path)[1]
    if ext != ".pyc":
        text = read_file_or_none(source_path)
        if text is not None:
            lines = text.split("\n")
            line_start = max(min_line - globs.context_line_count - 1, 0)
            line_end = min(len(lines), max_line + globs.context_line_count + 1)
            return {
                'text': "\n".join(lines[line_start:line_end]),
                'startLine': line_start + 1,
                'startColumn': 1,
                'path': source_path,
                'tabWidth': globs.tab_width,
            }
    return { 'path': source_path }

def collect_source_code(report, source_code_dict):
    out_source_code = {}
    for key in source_code_dict:
        item = source_code_dict[key]
        out_source_code[key] = create_source_object(item['path'], item['minLine'], item['maxLine'])
    report['sourceCode'] = out_source_code

def prepare_and_send_report(msg):
    globs.tab_width = msg['tab_width']
    globs.debug_backtrace = msg['debug_backtrace']
    globs.context_line_count = msg['context_line_count']

    report = msg['report']
    source_code = msg['source_code']
    collect_source_code(report, source_code)

    post_json(msg['endpoint'], report)

for line in sys.stdin:
    msg = json.loads(line)
    if msg['id'] == 'terminate':
        sys.exit(0)
    elif msg['id'] == 'send':
        prepare_and_send_report(msg)
    else:
        raise Exception("invalid message id", msg['id'])
