from .configs import *


class DataReceivedConfig:
    def __init__(self):
        self.data_saved_path = DATA_SAVED_PATH
        self.data_decode_exe_path = DATA_DECODE_EXE_PATH
        self.data_output_path = DATA_YUV_PATH


data_received_config = DataReceivedConfig()


