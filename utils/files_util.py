import os


class FilesUtil:
    def __init__(self, folder_path: str):
        """
        param folder_path: 编码后的bin文件所在文件夹位置(绝对路径)
        """
        self.folder_path = folder_path
        self.file_paths = os.listdir(folder_path)
        self.size = len(self.file_paths)

    def read_data(self):
        for file_path in self.file_paths:
            with open(os.path.join(self.folder_path, file_path), 'rb') as f:
                contents = f.read()
                yield contents, len(contents)
        yield False, -1


if __name__ == "__main__":
    filesUtil = FilesUtil(r"D:\Learning\多媒体技术应用\实验\SocketTransmission\resources")
    for i in filesUtil.read_data():
        print()
