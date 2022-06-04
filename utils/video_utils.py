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
            cv2.waitKey(25)


def YUV2RGB(Y, U, V, height, width):
    bgr_data = np.zeros((height, width, 3), dtype=np.uint8)
    V = np.repeat(V, 2, 0)
    V = np.repeat(V, 2, 1)
    U = np.repeat(U, 2, 0)
    U = np.repeat(U, 2, 1)

    c = (Y - np.array([16])) * 298
    d = U - np.array([128])
    e = V - np.array([128])

    r = (c + 409 * e + 128) // 256
    g = (c - 100 * d - 208 * e + 128) // 256
    b = (c + 516 * d + 128) // 256

    r = np.where(r < 0, 0, r)
    r = np.where(r > 255, 255, r)

    g = np.where(g < 0, 0, g)
    g = np.where(g > 255, 255, g)

    b = np.where(b < 0, 0, b)
    b = np.where(b > 255, 255, b)

    bgr_data[:, :, 2] = r
    bgr_data[:, :, 1] = g
    bgr_data[:, :, 0] = b

    return bgr_data




