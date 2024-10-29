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


def test_stack_trace_generation_from_background_thread():
    background_thread_name = "test_background"
    data_container = []

    def throw_in_background():
        try:
            failing_function()
        except:
            report = BacktraceReport()
            report.capture_last_exception()
            data = report.get_data()
            data_container.append(data)

    thread = threading.Thread(target=throw_in_background, name=background_thread_name)
    thread.start()
    thread.join()
    if data_container:
        data = data_container[0]
        faulting_thread = data["threads"][data["mainThread"]]
        assert faulting_thread["name"] != "MainThread"
        assert faulting_thread["name"] == background_thread_name
        assert faulting_thread["fault"] == True
        # make sure other threads are not marked as faulting threads
        for thread_id in data["threads"]:
            thread = data["threads"][thread_id]
            if thread["name"] == background_thread_name:
                continue
            assert thread["fault"] == False

    else:
        assert False


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
