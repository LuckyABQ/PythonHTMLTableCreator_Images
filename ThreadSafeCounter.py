import threading
import time


class ThreadSafeCounter(object):
    def __init__(self, modulo_print=1):
        self.value = 0
        self.modulo_print = modulo_print
        self._lock = threading.Lock()
        self.start_time = time.time()
        print("\rFiles created:", 0, end=" ")

    def increment(self):
        with self._lock:
            self.value += 1
        if self.value % self.modulo_print == 0:
            passed_time = time.time() - self.start_time
            files_per_seconds = "{0:0.2f}".format(self.value / passed_time)
            print("\rFiles created:", self.value, "| files per second:", f"{files_per_seconds} files/s", end=" ")
