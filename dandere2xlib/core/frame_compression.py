import copy
import logging

import time
from pathlib import Path

from threading import Thread
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path, get_wait_delay
from dandere2xlib.ffmpeg.video_frame_extractor import VideoFrameExtractor


class FrameCompression(Thread):

    def __init__(self, manager: D2xManagement):
        super().__init__()

        self.__manager = manager
        self.__loger = logging.getLogger()

    def start(self) -> None:

        for x in range(self.__manager.frame_count):
            while self.__manager.input_images_array[x] is None:
                time.sleep(0.001)

            frame = self.__manager.input_images_array[x]
            compressed = copy.deepcopy(frame)
            compressed.compress_frame_for_computations(100)
            self.__manager.compressed_frames_array[x] = compressed
