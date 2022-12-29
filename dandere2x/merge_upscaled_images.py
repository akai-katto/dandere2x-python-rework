import copy
import gc
import logging
import time
from pathlib import Path

from threading import Thread
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.ffmpeg.frames_to_video_pipe import FramesToVideoPipe
from dandere2xlib.models.d2x_residual_coordinate import D2xResidualCoordinate


class MergeUpscaledImages(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        self.dandere2x_session = dandere2x_session

        self._BLEED = 1
        self._HEIGHT = self.dandere2x_session.video_properties.corrected_video_height
        self._WIDTH = self.dandere2x_session.video_properties.corrected_video_width
        self._BLOCK_SIZE = self.dandere2x_session.block_size
        self._FRAME_COUNT = self.dandere2x_session.video_properties.input_video_settings.frame_count
        self._SCALE_FACTOR = self.dandere2x_session.scale_factor

        self.__manager = manager
        self.__loger = logging.getLogger()

    def run(self) -> None:

        current_frame = D2xFrame(self._WIDTH * self._SCALE_FACTOR, self._HEIGHT * self._SCALE_FACTOR)
        for pos in range(self._FRAME_COUNT):
            while self.__manager.residual_blocks[pos] is None:
                time.sleep(0.0001)
            while self.__manager.residual_images_upscaled[pos] is None:
                time.sleep(0.0001)

            while self.__manager.missing_blocks[pos] is None:
                time.sleep(0.0001)

            residual_undo = self.__manager.residual_blocks[pos]
            missing_blocks = self.__manager.missing_blocks[pos]
            residual_image: D2xFrame = copy.deepcopy(self.__manager.residual_images_upscaled[pos])

            if len(missing_blocks) == 0 and len(residual_undo) == 0:
                pass
            elif len(missing_blocks) != 0 and len(residual_undo) == 0:
                current_frame = residual_image
            else:
                for residual in residual_undo:
                    residual: D2xResidualCoordinate = residual
                    current_frame.copy_block(frame_other=residual_image,
                                             block_size=self._BLOCK_SIZE * self._SCALE_FACTOR,
                                             this_x=residual.x_start * self._SCALE_FACTOR,
                                             this_y=residual.y_start * self._SCALE_FACTOR,
                                             other_x=residual.residual_x * (self._BLOCK_SIZE + self._BLEED * 2)
                                                     * self._SCALE_FACTOR + (self._BLEED * self._SCALE_FACTOR),
                                             other_y=residual.residual_y * (self._BLOCK_SIZE + self._BLEED * 2)
                                                     * self._SCALE_FACTOR + (self._BLEED * self._SCALE_FACTOR))

            self.__manager.last_piped_frame = pos
            self.__manager.finished_frames[pos] = copy.deepcopy(current_frame)
