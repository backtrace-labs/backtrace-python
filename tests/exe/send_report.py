import os
import sys
import time

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


def do_the_thing():
    bt.send_report(
        "dsa", annotations={"color": "blue"}, attributes={"genre": "happy hardcore"}
    )


do_the_thing()
time.sleep(1)
