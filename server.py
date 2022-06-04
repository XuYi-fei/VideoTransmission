import socket
import os
import time
from configs import Config, DefaultConfig
from utils import FilesUtil, send_bytes, send_msg


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
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sk.bind((self.server_config.ip, self.server_config.port))
        self.sk.listen(10)
        # 编码后的视频文件数目
        self.video_file_size = size

    def start(self):
        # seq 标记发送的文件的序号
        seq = 1
        print("Waiting for a client to connect")
        self.client, address = self.sk.accept()
        print("Connected, ready to send controlling block")
        self.client.sendall(bytes(str(self.video_file_size).encode(encoding='utf-8')))
        self.client.close()
        while True:
            # time.sleep(2)
            # 等待连接
            print("Waiting for the client to apply for bitstream")
            self.client, address = self.sk.accept()
            # 打印连接的客户机地址
            print("ip is %s" % address[0])
            # 获取bin数据
            file_data, length = next(self.bin_files)
            info = {"seq": seq, "length": length}
            # 回应客户机连接建立成功
            res = send_msg(self.client, "connected!")
            # 判断当前是否还有码流文件未传输,如果没有了，通知客户端结束
            if not file_data:
                send_msg(self.client, "All of the data is sent!")
                break
            # 发送控制信息
            send_msg(self.client, str(info))
            seq += 1
            print("length", info['length'], "actual data length", len(file_data))
            # 发送文件
            sent_num = 0
            while sent_num < info['length']:
                send_bytes(self.client, file_data[sent_num:sent_num+4096])
                sent_num += 4096
            # 接收对方的确认消息但是不回复
        print("All of the data is sent!")
        self.sk.close()


def main():
    fileUtils = FilesUtil(os.path.join(os.path.abspath("."), Config.server_config.file_folder_path))
    files = fileUtils.read_data()
    socket_service = SocketService(Config, files, fileUtils.size)
    socket_service.start()


if __name__ == "__main__":
    while True:
        main()

