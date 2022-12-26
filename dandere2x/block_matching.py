import copy
import logging
import time

from threading import Thread

import numpy as np

from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay


class BlockMatching(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        self.dandere2x_session = dandere2x_session

        self._HEIGHT = self.dandere2x_session.video_properties.corrected_video_height
        self._WIDTH = self.dandere2x_session.video_properties.corrected_video_width
        self._BLOCK_SIZE = self.dandere2x_session.block_size

        self.__manager = manager
        self.__logger = logging.getLogger(dandere2x_session.input_video_path.name)

    def run(self) -> None:
        f1 = D2xFrame(self.dandere2x_session.video_properties.corrected_video_width,
                      self.dandere2x_session.video_properties.corrected_video_height)

        for frame_pos in range(0, self.dandere2x_session.video_properties.input_video_settings.frame_count - 1):

            while self.__manager.noised_images_array[frame_pos + 1] is None:
                time.sleep(get_wait_delay())

            while self.__manager.compressed_frames_array[frame_pos + 1] is None:
                time.sleep(get_wait_delay())

            f2 = copy.deepcopy(self.__manager.noised_images_array[frame_pos + 1])
            f2_compressed_raw = self.__manager.compressed_frames_array[frame_pos + 1]
            f2_compressed = (f2_compressed_raw.frame_array.astype(np.double) + f2.frame_array.astype(np.double))/2

            array_subtracted_squared: np.array = \
                np.power(f2.frame_array.astype(np.double) - f1.frame_array.astype(np.double), 2)
            compressed_subtracted_squared: np.array = \
                np.power(f2_compressed - f2.frame_array.astype(np.double), 2)

            matched_mean = np.einsum(
                "ijklm->ik",
                array_subtracted_squared.reshape(
                    int(self._HEIGHT / self._BLOCK_SIZE), self._BLOCK_SIZE,
                    int(self._WIDTH / self._BLOCK_SIZE), self._BLOCK_SIZE,
                    -1
                ),
                dtype=np.double,
            )

            compressed_mean = np.einsum(
                "ijklm->ik",
                compressed_subtracted_squared.reshape(
                    int(self._HEIGHT / self._BLOCK_SIZE), self._BLOCK_SIZE,
                    int(self._WIDTH / self._BLOCK_SIZE), self._BLOCK_SIZE,
                    -1
                ),
                dtype=np.double,
            )

            compared: np.array = (matched_mean * self.dandere2x_session.quality) - compressed_mean

            matched_blocks = []
            missing_blocks = []
            for y in range(int(self._HEIGHT / self._BLOCK_SIZE)):
                for x in range(int(self._WIDTH / self._BLOCK_SIZE)):
                    if compared[y][x] <= 0:
                        matched_blocks.append((x * self._BLOCK_SIZE, y * self._BLOCK_SIZE))
                    else:
                        missing_blocks.append((x * self._BLOCK_SIZE, y * self._BLOCK_SIZE))

            for matched_block in matched_blocks:
                x, y = matched_block
                f2.copy_block(f1, self._BLOCK_SIZE,
                              x, y,
                              x, y)

            f1 = copy.deepcopy(f2)
            self.__manager.missing_blocks[frame_pos] = missing_blocks