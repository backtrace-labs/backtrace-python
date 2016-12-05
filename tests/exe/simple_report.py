import sys, os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)
import backtracepython as bt

host, port = sys.argv[1:]

endpoint = "http://{}:{}".format(host, port)

bt.initialize(
    endpoint=endpoint,
    token="FakeToken",
    debug_backtrace=True,
    attributes={'a': 1, 'b': "bar"},
)

example_local_var = "hello this is my value"

a = b
