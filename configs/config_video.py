from .configs import *


class VideoConfig:
    def __init__(self):
        self.video_image_per_second = VIDEO_IMAGE_PER_SECOND
        self.video_height = DATA_HEIGHT
        self.video_width = DATA_WIDTH


video_config = VideoConfig()


