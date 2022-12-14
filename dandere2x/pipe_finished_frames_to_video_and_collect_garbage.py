import copy
import gc
import logging
import threading
import time
from pathlib import Path

from threading import Thread

from dandere2xlib.d2x_frame import D2xFrame
from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.d2x_management import D2xManagement
from dandere2xlib.d2x_suspend_management import Dandere2xSuspendManagement
from dandere2xlib.ffmpeg.frames_to_video_pipe import FramesToVideoPipe
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay


class PipeFinishedFramesToVideoAndCollectGarbage(Thread):

    def __init__(self,
                 manager: D2xManagement,
                 dandere2x_session: Dandere2xSession,
                 dandere2x_suspend_management: Dandere2xSuspendManagement):
        super().__init__()

        self._dandere2x_session = dandere2x_session
        self._dandere2x_suspend_management = dandere2x_suspend_management

        self._HEIGHT = self._dandere2x_session.video_properties.corrected_video_height
        self._WIDTH = self._dandere2x_session.video_properties.corrected_video_width
        self._BLOCK_SIZE = self._dandere2x_session.block_size
        self._FRAME_COUNT = self._dandere2x_session.video_properties.input_video_settings.frame_count


        self.__manager = manager
        self.__logger = logging.getLogger(dandere2x_session.input_video_path.name)

    def run(self) -> None:

        frames_to_pipe = FramesToVideoPipe(self._dandere2x_session.no_sound_video_file, self._dandere2x_session)
        frames_to_pipe.start()

        for pos in range(self._FRAME_COUNT):
            while self.__manager.finished_frames[pos] is None or self._dandere2x_suspend_management.is_suspended():
                time.sleep(get_wait_delay())

            piped_frame: D2xFrame = self.__manager.finished_frames[pos]
            frames_to_pipe.save(piped_frame)

            self.__manager.last_piped_frame = pos

            # Collect Garbage
            self.__manager.residual_images_upscaled[pos] = None
            self.__manager.missing_blocks[pos] = None
            self.__manager.compressed_frames_array[pos] = None
            self.__manager.noised_images_array[pos] = None
            self.__manager.input_images_array[pos] = None
            self.__manager.residual_images[pos] = None
            self.__manager.residual_blocks[pos] = None
            self.__manager.finished_frames[pos] = None

            n = gc.collect()
            #print("Number of unreachable objects collected by GC:", n)
            self.__logger.info(f"Piped frame {pos} of "
                               f"{self._dandere2x_session.video_properties.input_video_settings.frame_count}"
                               f" into output video.")

        frames_to_pipe.kill()
        frames_to_pipe.join()
