import sys
import os
import afile

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)
import backtracepython as bt

host, port = sys.argv[1:]

endpoint = "http://{}:{}".format(host, port)

bt.initialize(endpoint=endpoint, token="FakeToken", debug_backtrace=True)


def call_a_file(arg):
    if arg:
        afile.foo()


call_a_file(False)
call_a_file(True)
call_a_file(False)
