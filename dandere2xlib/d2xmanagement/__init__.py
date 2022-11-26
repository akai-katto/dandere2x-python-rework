import sys
from typing import Mapping, Set, Union

from dandere2xlib.d2xframe import D2xFrame

class D2xResidualCoordinate:

    def __init__(self, x_start, y_start, residual_x, residual_y):
        self.x_start = x_start
        self.y_start = y_start
        self.residual_x = residual_x
        self.residual_y = residual_y

class D2xManagement:

    def __init__(self, frame_count: int):

        self.frame_count = frame_count
        self.last_upscaled_frame = 0

        self.input_images_array: list[Union[D2xFrame, None]] = []
        for x in range(50000):
            self.input_images_array.append(None)

        self.noised_images_array: list[Union[D2xFrame, None]] = []
        for x in range(50000):
            self.noised_images_array.append(None)

        self.compressed_frames_array = []
        for x in range(50000):
            self.compressed_frames_array.append(None)

        self.missing_blocks = []
        for x in range(50000):
            self.missing_blocks.append(None)

        self.residual_blocks: list[Union[list[D2xResidualCoordinate], None]] = []
        for x in range(50000):
            self.residual_blocks.append(None)

        self.residual_images: list[Union[D2xFrame, None]] = []
        for x in range(50000):
            self.residual_images.append(None)

        self.residual_images_upscaled = []
        for x in range(50000):
            self.residual_images_upscaled.append(None)

        self.active_w2x = 0



if __name__ == "__main__":
    test = D2xManagement(239)