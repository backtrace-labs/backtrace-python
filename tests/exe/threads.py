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
    context_line_count=2,
)

import threading
import time


def thread_one():
    while True:
        time.sleep(0.1)

def thread_two():
    while True:
        time.sleep(0.2)

threading.Thread(target=thread_one, name="Uno", daemon=True).start()
threading.Thread(target=thread_one, name="Dos", daemon=True).start()
threading.Thread(target=thread_two, name="Tres", daemon=True).start()

this = broken
