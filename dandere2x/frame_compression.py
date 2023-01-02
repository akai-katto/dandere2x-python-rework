import copy
import logging

import time

from threading import Thread

from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.d2x_management import D2xManagement
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from dandere2xlib.ffmpeg.video_frame_extractor import VideoFrameExtractor
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


class FrameCompression(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        self.dandere2x_session = dandere2x_session

        self.__manager = manager
        self.__loger = logging.getLogger()

    def run(self) -> None:

        for pos in range(self.dandere2x_session.video_properties.input_video_settings.frame_count):

            while self.__manager.noised_images_array[pos] is None:
                time.sleep(get_wait_delay())

            frame = self.__manager.noised_images_array[pos]
            compressed = copy.deepcopy(frame)
            compressed.compress_frame_for_computations(100)
            self.__manager.compressed_frames_array[pos] = compressed
