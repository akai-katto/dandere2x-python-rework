import copy
import logging
import math
import time

from threading import Thread
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.models.d2x_residual_coordinate import D2xResidualCoordinate


class ResidualProcessing(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        # Interesting metadata
        self.pixels_upscaled_count = 0
        self.total_pixels_count = 0

        self.dandere2x_session = dandere2x_session

        self._HEIGHT = self.dandere2x_session.video_properties.corrected_video_height
        self._WIDTH = self.dandere2x_session.video_properties.corrected_video_width
        self._BLOCK_SIZE = self.dandere2x_session.block_size
        self._FRAME_COUNT = self.dandere2x_session.video_properties.input_video_settings.frame_count

        self.__manager = manager
        self.__loger = logging.getLogger()

    def run(self) -> None:
        BUFFER = 5
        BLEED = 1

        for pos in range(self._FRAME_COUNT):
            while self.__manager.missing_blocks[pos] is None:
                time.sleep(0.0001)
            while self.__manager.input_images_array[pos] is None:
                time.sleep(0.0001)

            missing_blocks = self.__manager.missing_blocks[pos]

            f1 = copy.deepcopy(self.__manager.input_images_array[pos])

            if len(missing_blocks) != 0:

                if len(missing_blocks) >= ((self._WIDTH / self._BLOCK_SIZE) * (self._HEIGHT / self._BLOCK_SIZE)) * .85:
                    residual_image = f1
                    self.__manager.residual_images[pos] = residual_image
                    self.__manager.residual_blocks[pos] = []
                    continue

                f1.create_buffered_image(BUFFER)
                dim = math.ceil(math.sqrt(len(missing_blocks))) + 1
                residual_image = D2xFrame(dim * (self._BLOCK_SIZE + BLEED * 2), dim * (self._BLOCK_SIZE + BLEED * 2))

                residual_undo = []
                x_dim = 0
                y_dim = 0
                for missing_block in missing_blocks:
                    x, y = missing_block
                    if x_dim >= dim:
                        x_dim = 0
                        y_dim += 1
                    residual_image.copy_block(f1, (self._BLOCK_SIZE + BLEED * 2),
                                              x + BUFFER - BLEED, y + BUFFER - BLEED,
                                              x_dim * (self._BLOCK_SIZE + BLEED * 2), y_dim * (self._BLOCK_SIZE + BLEED * 2))

                    residual_undo.append(
                        D2xResidualCoordinate(x_start=x, y_start=y, residual_x=x_dim, residual_y=y_dim))
                    x_dim += 1

                self.__manager.residual_blocks[pos] = residual_undo
            else:
                residual_image = D2xFrame(1, 1)
                self.__manager.residual_blocks[pos] = []

            self.__manager.residual_images[pos] = residual_image

            # metadata
            self.pixels_upscaled_count += residual_image.width * residual_image.height
            self.total_pixels_count += f1.width * f1.height
