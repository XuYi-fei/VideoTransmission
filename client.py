import os
import socket
from configs import Config, DefaultConfig
from threading import Thread
from utils import DataQueue, SlidingWindow
import subprocess


class DataManagement(Thread):
    def __init__(self, size):
        super(DataManagement, self).__init__()
        self.config = Config.data_received_config
        self.exe_path = os.path.join(os.getcwd(), self.config.data_decode_exe_path)
        # 检测存放bin、yuv数据的文件夹是否存在，若不存在就创建
        self.saved_dir = os.path.join(os.getcwd(), self.config.data_saved_path)
        self.output_dir = os.path.join(os.getcwd(), self.config.data_output_path)
        self.received_num = 0
        self.max_received_num = size
        if not os.path.exists(self.saved_dir):
            os.makedirs(self.saved_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def run(self) -> None:
        global if_trans_finished
        while True:
            seq, data = data_queue.get()
            if if_trans_finished and self.received_num >= self.max_received_num:
                break
            if data is None:
                continue
            self.received_num += 1
            with open(os.path.join(self.saved_dir, str(seq) + '.bin'), 'wb') as f:
                f.write(data)
            frame_queue.put(seq, str(seq) + '.yuv')
            command = self.exe_path + " -b " + os.path.join(self.saved_dir, str(seq) + '.bin') \
                        + " -o " + os.path.join(self.output_dir, str(seq) + '.yuv')
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)


class SocketService(Thread):
    def __init__(self, config: DefaultConfig):
        super(SocketService, self).__init__()
        self.client_config = config.client_config
        self.server_config = config.server_config
        # 初始化socket属性
        self.sk = socket.socket()

    def run(self):
        self.sk.connect((self.server_config.ip, self.server_config.port))
        res = str(self.sk.recv(2048).decode(encoding='utf-8'))
        if res == "connected!":
            print("Connected to server!")
            self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
        data = bytes()
        num = 0
        info = self.sk.recv(1024).decode(encoding='utf-8')
        print(info)
        if info == "All of the data is sent!":
            self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
            self.sk.close()
            return
        # 获取到这个字典中的信息
        info = eval(info)
        self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
        while num < int(info['length']):
            data += self.sk.recv(1024)
            num += 1024
        self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
        self.sk.close()
        data_queue.put(int(info['seq']), data)


def main():
    # 先建立连接，确定接受的数据有多少个文件
    sk = socket.socket()
    sk.connect((Config.server_config.ip, Config.server_config.port))
    res = str(sk.recv(2048).decode(encoding='utf-8'))
    sk.close()
    # 开启DataManagement线程，监听优先队列内的数据
    data_thread = DataManagement(int(res))
    data_thread.start()
    # 开启多个线程
    socket_threads = []
    for i in range(int(res) + 1):
        socket_thread = SocketService(Config)
        socket_thread.start()
        socket_threads.append(socket_thread)
    for socket_thread in socket_threads:
        socket_thread.join()
    global if_trans_finished
    if_trans_finished = True
    data_thread.join()


if __name__ == "__main__":
    data_queue = DataQueue()
    frame_queue = DataQueue()
    sliding_window = SlidingWindow(frame_queue)
    if_trans_finished = False
    main()
