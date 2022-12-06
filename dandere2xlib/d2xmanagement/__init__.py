import sys

from typing import Mapping, Set, Union, List

from dandere2xlib.d2xframe import D2xFrame


class D2xResidualCoordinate:

    def __init__(self, x_start, y_start, residual_x, residual_y):
        self.x_start = x_start
        self.y_start = y_start
        self.residual_x = residual_x
        self.residual_y = residual_y


MAX_FRAMES = 50000000

class D2xManagement:

    def __init__(self):

        self.last_piped_frame = 0

        self.input_images_array: list[Union[D2xFrame, None]] = []
        for x in range(MAX_FRAMES):
            self.input_images_array.append(None)

        self.noised_images_array: list[Union[D2xFrame, None]] = []
        for x in range(MAX_FRAMES):
            self.noised_images_array.append(None)

        self.compressed_frames_array = []
        for x in range(MAX_FRAMES):
            self.compressed_frames_array.append(None)

        self.missing_blocks = []
        for x in range(MAX_FRAMES):
            self.missing_blocks.append(None)

        self.residual_blocks: list[Union[List[D2xResidualCoordinate], None]] = []
        for x in range(MAX_FRAMES):
            self.residual_blocks.append(None)

        self.residual_images: list[Union[D2xFrame, None]] = []
        for x in range(MAX_FRAMES):
            self.residual_images.append(None)

        self.residual_images_upscaled = []
        for x in range(MAX_FRAMES):
            self.residual_images_upscaled.append(None)

        self.finished_frames: list[Union[D2xFrame, None]] = []
        for x in range(MAX_FRAMES):
            self.finished_frames.append(None)


if __name__ == "__main__":
    test = D2xManagement()
