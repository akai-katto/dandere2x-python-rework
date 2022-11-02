import sys
from typing import Mapping, Set, Union

from dandere2xlib.d2xframe import D2xFrame


class D2xManagement:

    def __init__(self):

        self.input_images_array: list[Union[D2xFrame, None]] = []
        for x in range(50000):
            self.input_images_array.append(None)

        self.compressed_frames_array = []
        for x in range(50000):
            self.compressed_frames_array.append(None)

        self.missing_blocks = []
        for x in range(50000):
            self.missing_blocks.append(None)

        self.residual_blocks = []
        for x in range(50000):
            self.residual_blocks.append(None)



if __name__ == "__main__":
    test = D2xManagement()
