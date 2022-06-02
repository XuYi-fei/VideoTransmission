import queue
import threading


class DataQueue:
    def __init__(self, size=10):
        self.size = size
        self.queue = queue.PriorityQueue(maxsize=self.size)
        self.current_size = 0
        self.lock = threading.Lock()

    def full(self):
        return self.current_size >= self.size

    def put(self, seq, data):
        self.lock.acquire()
        self.queue.put((seq, data))
        self.lock.release()
        self.current_size += 1

    def get(self):
        if self.current_size <= 0:
            return None, None
        self.lock.acquire()
        item = self.queue.get()
        self.lock.release()
        self.current_size -= 1
        return item

