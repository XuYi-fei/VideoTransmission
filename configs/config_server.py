from .configs import *


class ServerConfig:
    def __init__(self):
        self.port = SERVER_PORT
        self.ip = SERVER_IP
        self.file_folder_path = SERVER_FILE_FOLDER_PATH


server_config = ServerConfig()


