import logging
import time

from threading import Thread

from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from dandere2xlib.ffmpeg.video_frame_extractor import VideoFrameExtractor
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


class NoisedFrameExtraction(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        self.dandere2x_session = dandere2x_session

        self.__manager = manager
        self.__extractor = VideoFrameExtractor(ffmpeg_binary=load_executable_paths_yaml()['ffmpeg'],
                                               input_video=dandere2x_session.input_video_path,
                                               width=dandere2x_session.video_properties.corrected_video_width,
                                               height=dandere2x_session.video_properties.corrected_video_height,
                                               dandere2x_session=dandere2x_session,
                                               optional_args=["-vf", "noise=c1s=8:c0f=u"])
        self.__loger = logging.getLogger()

    def run(self) -> None:

        for pos in range(self.dandere2x_session.video_properties.input_video_settings.frame_count):

            while pos > self.__manager.last_piped_frame + 60:
                time.sleep(get_wait_delay())

            frame = self.__extractor.get_frame()
            self.__manager.noised_images_array[pos] = frame
