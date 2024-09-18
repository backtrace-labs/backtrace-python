import sys
import threading
import time

from backtracepython.report import BacktraceReport


def open_file(name):
    open(name).read()


def failing_function():
    open_file("test")


def test_main_thread_generation_without_exception():
    report = BacktraceReport()
    data = report.get_data()
    stack_trace = data["threads"][data["mainThread"]]
    assert len(stack_trace["stack"]) != 0


def test_skipping_backtrace_module_in_process_stack():
    test_name = sys._getframe().f_code.co_name

    report = BacktraceReport()
    data = report.get_data()
    stack_trace = data["threads"][data["mainThread"]]

    current_function_name = stack_trace["stack"][0]["funcName"]
    assert current_function_name == test_name


def test_main_thread_generation_with_exception():
    # this funciton + 2 fauulting functions
    expected_number_of_frames = 3
    try:
        failing_function()
    except:
        report = BacktraceReport()
        report.capture_last_exception()
        data = report.get_data()
        stack_trace = data["threads"][data["mainThread"]]
        assert len(stack_trace["stack"]) == expected_number_of_frames


def test_background_thread_stack_trace_generation():
    if_stop = False

    def wait_in_thread():
        while not if_stop:
            time.sleep(0.1)

    def runner():
        wait_in_thread()

    thread = threading.Thread(target=runner, name="runner")
    thread.start()

    report = BacktraceReport()
    data = report.get_data()
    if_stop = True
    thread.join()
    stack_trace = data["threads"][str(thread.ident)]
    assert len(stack_trace) != 0
