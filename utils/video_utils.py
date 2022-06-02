from threading import Thread


class SlidingWindow(Thread):
    def __init__(self, frame_queue):
        super(SlidingWindow, self).__init__()
        self.current_seq = 0
        self.frame_queue = frame_queue

    def run(self) -> None:
        while True:
            pass


