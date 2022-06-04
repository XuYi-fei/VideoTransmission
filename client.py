import os
import socket
from configs import Config, DefaultConfig
from threading import Thread
from utils import DataQueue, FrameDict, SlidingWindow
import subprocess
import cv2
import numpy as np


class VideoDecode(Thread):
    def __init__(self, command, output_dir, data_frame_per_yuv, seq, file_name, width, height):
        super(VideoDecode, self).__init__()
        self.output_dir = output_dir
        self.command = command
        self.seq = seq
        self.file_name = file_name
        self.width = width
        self.data_frame_per_yuv = data_frame_per_yuv
        self.height = height

    def run(self) -> None:
        # p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE)
        # print(self.command)
        # p.communicate()
        self.yuv2bgr(self.seq, os.path.join(self.output_dir, str(self.seq) + '.yuv'), self.width,
                     self.height)

    def yuv2bgr(self, seq, file_name, width, height, start_frame=0):
        imgs = []
        with open(file_name, 'rb') as fp:
            frame_size = height * width * 3 // 2  # 一帧图像所含的像素个数
            h_h = height // 2
            h_w = width // 2

            fp.seek(0, 2)  # 设置文件指针到文件流的尾部
            ps = fp.tell()  # 当前文件指针位置
            num_frame = ps // frame_size  # 计算输出帧数
            fp.seek(frame_size * start_frame, 0)
            for i in range(num_frame - start_frame):
                Yt = np.zeros(shape=(height, width), dtype='uint8', order='C')
                Ut = np.zeros(shape=(h_h, h_w), dtype='uint8', order='C')
                Vt = np.zeros(shape=(h_h, h_w), dtype='uint8', order='C')

                for m in range(height):
                    for n in range(width):
                        Yt[m, n] = ord(fp.read(1))
                for m in range(h_h):
                    for n in range(h_w):
                        Ut[m, n] = ord(fp.read(1))
                for m in range(h_h):
                    for n in range(h_w):
                        Vt[m, n] = ord(fp.read(1))

                img = np.concatenate((Yt.reshape(-1), Vt.reshape(-1), Ut.reshape(-1)))
                img = img.reshape((height * 3 // 2, width)).astype('uint8')
                bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YV12)
                imgs.append(bgr_img)

            for i, img in enumerate(imgs):
                print(len(frame_dict))
                frame_dict.put((seq-1) * self.data_frame_per_yuv + i + 1, img)


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
        decode_threads = []
        while True:
            seq, data = data_queue.get()
            if if_trans_finished and self.received_num >= self.max_received_num:
                break
            if data is None:
                continue
            self.received_num += 1
            with open(os.path.join(self.saved_dir, str(seq) + '.bin'), 'wb') as f:
                f.write(data)
            command = self.exe_path + " -b " + os.path.join(self.saved_dir, str(seq) + '.bin') \
                        + " -o " + os.path.join(self.output_dir, str(seq) + '.yuv')
            decode_thread = VideoDecode(command, self.output_dir, self.config.data_frame_per_yuv, seq,
                                        os.path.join(self.output_dir, str(seq)+'.yuv'), self.config.data_frame_width, self.config.data_frame_height)
            decode_thread.start()
            # decode_threads.append(decode_thread)
        # for sub_thread in decode_threads:
        #     sub_thread.start()
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            print(command)
            p.communicate()
            # video_info = {"seq": seq, "file_name": os.path.join(self.output_dir, str(seq)+'.yuv'), "width": self.config.data_frame_width,
            #               "height": self.config.data_frame_height }
            # frame_dict.put(seq, video_info)
            # self.yuv2bgr(seq, os.path.join(self.output_dir, str(seq)+'.yuv'), self.config.data_frame_width,
            #              self.config.data_frame_height)

    def yuv2bgr(self, seq, file_name, width, height, start_frame=0):
        imgs = []
        with open(file_name, 'rb') as fp:
            frame_size = height * width * 3 // 2  # 一帧图像所含的像素个数
            h_h = height // 2
            h_w = width // 2

            fp.seek(0, 2)  # 设置文件指针到文件流的尾部
            ps = fp.tell()  # 当前文件指针位置
            num_frame = ps // frame_size  # 计算输出帧数
            fp.seek(frame_size * start_frame, 0)
            for i in range(num_frame - start_frame):
                Yt = np.zeros(shape=(height, width), dtype='uint8', order='C')
                Ut = np.zeros(shape=(h_h, h_w), dtype='uint8', order='C')
                Vt = np.zeros(shape=(h_h, h_w), dtype='uint8', order='C')

                for m in range(height):
                    for n in range(width):
                        Yt[m, n] = ord(fp.read(1))
                for m in range(h_h):
                    for n in range(h_w):
                        Ut[m, n] = ord(fp.read(1))
                for m in range(h_h):
                    for n in range(h_w):
                        Vt[m, n] = ord(fp.read(1))

                img = np.concatenate((Yt.reshape(-1), Vt.reshape(-1), Ut.reshape(-1)))
                img = img.reshape((height * 3 // 2, width)).astype('uint8')
                bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YV12)
                imgs.append(bgr_img)
            for i, img in enumerate(imgs):
                frame_dict.put((seq-1) * self.config.data_frame_per_yuv + i + 1, img)


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
    global frame_dict
    sliding_window = SlidingWindow(frame_dict, Config.video_config)
    sliding_window.start()
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
    frame_dict = FrameDict()

    if_trans_finished = False
    main()
