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


class FrameDict:
    def __init__(self):
        self.next_index = 1
        self.get_index = 1
        self.lock = threading.Lock()
        self.frame = {}
        self.start = False

    def __len__(self):
        return len(self.frame)

    def if_start(self) -> bool:
        return self.start or len(self) > 100

    def put(self, seq, data):
        self.lock.acquire()
        self.frame[seq] = data
        while True:
            if self.next_index in self.frame:
                self.next_index += 1
            else:
                break
        self.lock.release()

    def get(self):
        if self.get_index >= self.next_index:
            return None
        self.lock.acquire()
        item = self.frame[self.get_index]
        self.get_index += 1
        self.lock.release()
        return item
