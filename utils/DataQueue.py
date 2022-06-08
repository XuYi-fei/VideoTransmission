import queue
import threading
from loguru import logger


class DataQueue:
    def __init__(self, size=10):
        """
        :param size: 此次视频传输的视频段数量
        """
        self.size = size
        self.queue = queue.PriorityQueue(maxsize=self.size)
        self.current_size = 0
        self.lock = threading.Lock()

    def full(self):
        return self.current_size >= self.size

    def put(self, seq, data):
        """
        :param seq: 放入队列的数据优先级，越小优先级越高
        :param data: 放入队列的数据
        :return:
        """
        self.lock.acquire()
        self.queue.put((seq, data))
        self.lock.release()
        self.current_size += 1

    def get(self):
        """
        :return: 如果当前的队列大小小于1，返回空，否则返回数据
        """
        if self.current_size <= 0:
            return None, None
        self.lock.acquire()
        item = self.queue.get()
        self.lock.release()
        self.current_size -= 1
        return item


class FrameDict(object):

    def __init__(self):
        # 按顺序下一个希望收到的帧
        self.next_index = 1
        # 下一个将要播放的帧
        self.get_index = 1
        self.lock = threading.Lock()
        self._ab = 1
        self.frame = {}
        self.end = False

    def __len__(self):
        return len(self.frame)

    def data_end(self):
        self.end = True

    def if_end(self) -> bool:
        """
        :return: 判断是否播放结束
        """
        return self.end and self.get_index >= self.next_index

    def put(self, seq, data):
        """
        :param seq: 放入字典的key，代表帧序号
        :param data: 放入字典的帧
        :return:
        """
        self.lock.acquire()
        self.frame[seq] = data
        while True:
            # 更新next_index
            if self.next_index in self.frame:
                self.next_index += 1
            else:
                break
        self.lock.release()

    def get(self):
        logger.debug("[dict_length]: [%d] | [get_index]: [%d] | [next_index]: [%d]" % (len(self.frame), self.get_index, self.next_index))
        if self.get_index >= self.next_index:
            return None
        self.lock.acquire()
        # 取出下一个播放帧并更新响应属性
        item = self.frame[self.get_index]
        del self.frame[self.get_index]
        self.get_index += 1
        self.lock.release()
        return item
