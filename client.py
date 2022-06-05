import os
import sys
import socket
import threading
from configs import Config, DefaultConfig
from threading import Thread
from utils import DataQueue, FrameDict, SlidingWindow, create_folder, send_msg_no_recv, YUV2RGB
import subprocess
import numpy as np
from loguru import logger
logger.remove()
logger.add(sys.stdout,
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{'
                  'message}</level>',
           level=Config.log_config.log_level)

received_num = 0
con = threading.Condition()


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
            seq, data = data_queue.get()
            if received_num >= self.max_received_num:
                con.release()
                break
            if data is None:
                con.wait()
                con.release()
                continue
            received_num += 1
            con.release()
            self.yuv2bgr(seq, data)

    def from_I420(self, yuv_data, frames):
        """
        从yuv文件中解析得到Y、U、V分量
        :param yuv_data:
        :param frames:
        :return: Y、U、V分量
        """
        Y = np.zeros((frames, self.config.data_frame_height, self.config.data_frame_width), dtype=np.uint8)
        U = np.zeros((frames, int(self.config.data_frame_height / 2), int(self.config.data_frame_width / 2)), dtype=np.uint8)
        V = np.zeros((frames, int(self.config.data_frame_height / 2), int(self.config.data_frame_width / 2)), dtype=np.uint8)

        for frame_idx in range(0, frames):
            y_start = frame_idx * self.config.video_image_size
            u_start = y_start + self.config.data_frame_height * self.config.data_frame_width
            v_start = u_start + int(self.config.data_frame_height * self.config.data_frame_width / 4)
            v_end = v_start + int(self.config.data_frame_height * self.config.data_frame_width / 4)

            Y[frame_idx, :, :] = yuv_data[y_start: u_start].reshape(
                (self.config.data_frame_height, self.config.data_frame_width))
            U[frame_idx, :, :] = yuv_data[u_start: v_start].reshape(
                (int(self.config.data_frame_height / 2), int(self.config.data_frame_width / 2)))
            V[frame_idx, :, :] = yuv_data[v_start: v_end].reshape(
                (int(self.config.data_frame_height / 2), int(self.config.data_frame_width / 2)))
        return Y, U, V

    def yuv2bgr(self, seq, file_name):
        """
        将读入的yuv数据转化为bgr的img存入列表
        :param seq: yuv文件序号
        :param file_name: yuv文件路径
        :return: None
        """
        imgs = []
        with open(file_name, 'rb') as f:
            data = np.frombuffer(f.read(), np.uint8)
        Y, U, V = self.from_I420(data, self.config.data_frame_per_yuv)
        for frame_idx in range(self.config.data_frame_per_yuv):
            bgr_data = YUV2RGB(Y[frame_idx, :, :], U[frame_idx, :, :], V[frame_idx, :, :], self.config.data_frame_height, self.config.data_frame_width)           # numpy
            if bgr_data is not None:
                imgs.append(bgr_data)
        for i, img in enumerate(imgs):
            frame_dict.put((seq - 1) * self.config.data_frame_per_yuv + i + 1, img)


class SocketService(Thread):
    def __init__(self, config: DefaultConfig):
        """
        :param config: 配置变量
        """
        super(SocketService, self).__init__()
        # 获取需要的配置
        self.client_config = config.client_config
        self.data_config = config.data_received_config
        self.server_config = config.server_config
        self.absolute_path = os.getcwd()
        self.saved_dir, self.output_dir, self.exe_path = self.get_paths()
        create_folder(self.saved_dir, self.output_dir)

    def get_paths(self):
        """
        :return: 获得三个拼接路径——bin文件存储路径、yuv存储路径、解码exe路径
        """
        return os.path.join(self.absolute_path, self.data_config.data_saved_path), \
               os.path.join(self.absolute_path, self.data_config.data_output_path), \
               os.path.join(self.absolute_path, self.data_config.data_decode_exe_path)

    def get_cmd(self, seq: str) -> str:
        """
        :param seq: 当前文件的序号
        :return: 生成的命令行命令
        """
        return self.exe_path + " -b " + os.path.join(self.saved_dir, seq + '.bin') + " -o " + \
               os.path.join(self.output_dir, seq + '.yuv')

    def run(self):
        global con
        logger.success("||############   Video transmit begin.    ############||")
        while True:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sk.connect((self.server_config.ip, self.server_config.port))
            res = str(self.sk.recv(2048).decode(encoding='utf-8'))
            if res == "connected!":
                send_msg_no_recv(self.sk, "ok")
            data, num = bytes(), 0
            info = self.sk.recv(1024).decode(encoding='utf-8')
            if info == "All of the data is sent!":
                logger.success("||##########   Video transmitted over.      ##########||")
                send_msg_no_recv(self.sk, "ok")
                frame_dict.data_end()
                self.sk.close()
                break
            info = eval(info)
            logger.success("|| Connected to the server. Begin to receive packets. ||")
            logger.info("Info of data to receive:")
            logger.info("[Seq]: [No.%d] | [Data Size]: [%d] bytes" % (info['seq'], info['length']) )
            # 获取到这个字典中的信息
            send_msg_no_recv(self.sk, "ok")
            while num <= int(info['length']):
                data += self.sk.recv(4096)
                num += 4096
                send_msg_no_recv(self.sk, "ok")
                logger.info("Transmitting... | [Seq]: [No.%d] | [Received Size / Data Size]: [%d]/[%d] bytes"
                            % (info['seq'],  len(data), info['length']))
            logger.success("----     Bitstream received. Closing the socket     ----")
            # 保存为bin文件
            with open(os.path.join(self.saved_dir, str(info['seq']) + '.bin'), 'wb') as f:
                f.write(data)
            # 解码为yuv文件
            command = self.get_cmd(str(info['seq']))
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            p.communicate()
            con.acquire()
            data_queue.put(info['seq'], os.path.join(self.output_dir, str(info['seq']) + '.yuv'))
            con.notify_all()
            con.release()


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
    decode_thread.join()
    clean_up()


def clean_up():
    if os.path.exists("./num.csv"):
        os.remove("./num.csv")
    if os.path.exists("./dec1.csv"):
        os.remove("./dec1.csv")


if __name__ == "__main__":
    data_queue = DataQueue()
    frame_dict = FrameDict()
    if_trans_finished = False
    main()
