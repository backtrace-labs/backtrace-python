import multiprocessing
import os
import socket
import sys
import time

from backtracepython.attributes.attribute_provider import AttributeProvider

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ProcessAttributeProvider(AttributeProvider):
    def __init__(self):
        self.process_start_time = time.time()
        current_process = multiprocessing.current_process()
        self.attributes = {
            'application': current_process.name,
            'process.id': os.getpid(),
            'hostname': socket.gethostname(),
        }

    def get(self):
        result = {}
        result.update(self.attributes)
        result.update({
            'process.age': int(time.time() - self.process_start_time)
        })

        return result