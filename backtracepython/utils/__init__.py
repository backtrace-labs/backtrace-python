import json
import logging
import re

def parse_json(data, log_warning=True):
    """Parses JSON from string. This uses the standard library json.dumps, but also adds
    support for parsing illegal JSON values as null.
    When illegal JSON characters (Nan, -Infinity, and Infinity) a warning log is emitted.
    """
    try:
        return json.dumps(data, allow_nan=False)
    except:
        # warn user that they are passing invalid data. Parse with illegal JSON and regex replace with `null`.
        if log_warning:
            logging.warning('Illegal JSON values (NaN, -Infinity, and Infinity) will be parsed as nulls. Avoid passing these values in attributes. Read more here: https://docs.python.org/3/library/json.html')
        return re.sub(r': (NaN|Infinity|-Infinity),?\b', ': null', json.dumps(data, allow_nan=True))
