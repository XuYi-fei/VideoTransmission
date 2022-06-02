from .config_client import client_config
from .config_server import server_config
from .config_received_data import data_received_config

class DefaultConfig:
    def __init__(self):
        self.server_config = server_config
        self.client_config = client_config
        self.data_received_config = data_received_config


Config = DefaultConfig()
