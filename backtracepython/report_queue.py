import sys
import threading

if sys.version_info.major >= 3:
    import queue
else:
    import Queue as queue


class ReportQueue:
    def __init__(self, request_handler, source_code_handler=None):
        self.request_handler = request_handler
        self.source_code_handler = source_code_handler

        # report submission tasks queue
        self.report_queue = queue.Queue()

        # Create and start a single worker thread
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.active = True
        self.worker_thread.start()

    def _worker(self):
        while True:
            report_data = self.report_queue.get()
            if report_data is None or self.active == False:
                self.report_queue.task_done()
                break
            report, attachments = report_data
            self.process(report, attachments)
            self.report_queue.task_done()

    def add(self, report, attachments):
        self.report_queue.put_nowait((report, attachments))

    # Immediately process the report and skip the queue process
    # Use this method to handle importa data before application exit
    def process(self, report, attachments):
        if self.source_code_handler is not None:
            self.source_code_handler.collect(report)
        self.request_handler.send(report, attachments)

    def __del__(self):
        self.dispose()

    def dispose(self):
        # Put a sentinel value to stop the worker thread
        self.active = False
        self.report_queue.put_nowait(None)
        self.report_queue.join()
        self.worker_thread.join()
