import socket
import queue
import os
from configs import Config, DefaultConfig
from utils import FilesUtil
msg_queue = queue.Queue(maxsize=250)


class SocketService:
    def __init__(self, config: DefaultConfig, bin_files, size):
        """
        :param config: 全局配置
        :param bin_files: 一个所读入的二进制文件的生成器
        :param size: 确定下来的二进制文件个数
        """
        self.bin_files = bin_files
        self.client_config = config.client_config
        self.server_config = config.server_config
        # 初始化socket属性
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk.bind((self.server_config.ip, self.server_config.port))
        self.sk.listen(10)
        # 编码后的视频文件数目
        self.video_file_size = size

    def start(self):
        # seq 标记发送的文件的序号
        seq = 1
        print("waiting for connection1......")
        self.client, address = self.sk.accept()
        print("connected!")
        self.client.sendall(bytes(str(self.video_file_size).encode(encoding='utf-8')))
        self.client.close()
        while True:
            # 等待连接
            print("waiting for connection......")
            self.client, address = self.sk.accept()
            print("connected!")
            # 打印连接的客户机地址
            print("ip is %s" % address[0])
            # 回应客户机连接建立成功
            self.client.sendall(bytes("connected!".encode(encoding='utf-8')))
            file_data, length = next(self.bin_files)
            info = {"seq": seq, "length": length}
            res = self.client.recv(1024).decode(encoding='utf-8')
            print('1: ', res)
            if res == "ok":
                if not file_data:
                    self.client.sendall(bytes("All of the data is sent!".encode(encoding='utf-8')))
                    # 接收对方的确认消息但不回复
                    self.client.recv(1024)
                    break
                else:
                    self.client.sendall(bytes(str(info).encode(encoding='utf-8')))
            seq += 1
            res = self.client.recv(1024).decode(encoding='utf-8')
            print('2: ', res)
            if res == "ok":
                self.client.sendall(file_data)
            # 接收对方的确认消息但是不回复
            self.client.recv(1024).decode(encoding='utf-8')
        print("All of the data is sent!")

    def update_service(self):
        pass


def main():
    fileUtils = FilesUtil(os.path.join(os.path.abspath("."), Config.server_config.file_folder_path))
    files = fileUtils.read_data()
    socket_service = SocketService(Config, files, fileUtils.size)
    socket_service.start()


if __name__ == "__main__":
    while True:
        main()

