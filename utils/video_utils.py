from threading import Thread
import numpy as np
import cv2

from .DataQueue import FrameDict


class SlidingWindow(Thread):
    def __init__(self, frame_dict: FrameDict, config):
        super(SlidingWindow, self).__init__()
        self.video_config = config
        self.frame_dict = frame_dict
        self.current_seq = 0

    def run(self) -> None:
        img = np.zeros((self.video_config.video_height, self.video_config.video_width, 3))
        while True:
            new_img = self.frame_dict.get()
            text = "" if new_img is not None else "buffering...."
            img = new_img if new_img is not None else img
            cv2.putText(img, text,
                        (self.video_config.video_height // 5, self.video_config.video_width // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
            cv2.imshow("video", img)
            cv2.waitKey(50)






