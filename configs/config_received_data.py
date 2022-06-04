from .configs import *


class DataReceivedConfig:
    def __init__(self):
        self.data_saved_path = DATA_SAVED_PATH
        self.data_decode_exe_path = DATA_DECODE_EXE_PATH
        self.data_output_path = DATA_YUV_PATH
        self.data_frame_per_yuv = DATA_FRAME_PER_YUV
        self.data_frame_width = DATA_WIDTH
        self.data_frame_height = DATA_HEIGHT
        self.video_image_size = DATA_IMAGE_SIZE


data_received_config = DataReceivedConfig()


