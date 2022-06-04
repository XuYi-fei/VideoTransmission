import os
import socket
import threading
from configs import Config, DefaultConfig
from threading import Thread
from utils import DataQueue, FrameDict, SlidingWindow, create_folder
import subprocess
import cv2
import numpy as np
received_num = 0
con = threading.Condition()
yuv_num = 0


class DataManagement(Thread):
    def __init__(self, size):
        super(DataManagement, self).__init__()
        self.config = Config.data_received_config
        self.max_received_num = size

    def run(self) -> None:
        global if_trans_finished
        global received_num
        global con
        while True:
            con.acquire()
            # print("data: ", con)
            seq, data = data_queue.get()
            if if_trans_finished and received_num >= self.max_received_num:
                con.release()
                # print("data: released", con)
                break
            if data is None:
                # print("data: waiting", con)
                con.wait()
                con.release()
                # print("data: waiting over", con)
                continue
            received_num += 1
            con.release()
            # print("data: released", con)
            self.yuv2bgr(seq, data, self.config.data_frame_width, self.config.data_frame_height, 0)

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
        # 获取需要的配置
        self.client_config = config.client_config
        self.data_config = config.data_received_config
        self.server_config = config.server_config
        self.saved_dir = os.path.join(os.getcwd(), self.data_config.data_saved_path)
        self.output_dir = os.path.join(os.getcwd(), self.data_config.data_output_path)
        self.exe_path = os.path.join(os.getcwd(), self.data_config.data_decode_exe_path)
        create_folder(self.saved_dir)
        create_folder(self.output_dir)

    def run(self):
        global con
        while True:
            self.sk = socket.socket()
            self.sk.connect((self.server_config.ip, self.server_config.port))
            res = str(self.sk.recv(2048).decode(encoding='utf-8'))
            if res == "connected!":
                print("Connected to server!")
                self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
            data, num = bytes(), 0
            info = self.sk.recv(1024).decode(encoding='utf-8')
            print(info)
            if info == "All of the data is sent!":
                self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
                self.sk.close()
                break
            # 获取到这个字典中的信息
            info = eval(info)
            self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
            while num < int(info['length']):
                data += self.sk.recv(1024)
                num += 1024
            self.sk.sendall(bytes("ok".encode(encoding='utf-8')))
            # 保存为bin文件
            with open(os.path.join(self.saved_dir, str(info['seq']) + '.bin'), 'wb') as f:
                f.write(data)
            # 解码为yuv文件
            command = self.exe_path + " -b " + os.path.join(self.saved_dir, str(info['seq']) + '.bin') \
                      + " -o " + os.path.join(self.output_dir, str(info['seq']) + '.yuv')
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            p.communicate()
            con.acquire()
            # print("socket: acquired", con)
            data_queue.put(info['seq'], os.path.join(self.output_dir, str(info['seq']) + '.yuv'))
            con.notify_all()
            # print("socket: notified", con)
            con.release()
            # print("socket: released", con)


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
    decode_thread = DataManagement(int(res))
    decode_thread.start()
    # 开启网络传输线程
    socket_thread = SocketService(Config)
    socket_thread.start()
    socket_thread.join()
    # 标志传输结束
    global if_trans_finished
    if_trans_finished = True
    decode_thread.join()


if __name__ == "__main__":
    data_queue = DataQueue()
    frame_dict = FrameDict()
    if_trans_finished = False
    main()
