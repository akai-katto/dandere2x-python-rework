import sys


from typing import Mapping, Set, Union, List, Dict
from collections import defaultdict
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

        self.input_images_array: Dict[Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.noised_images_array: Dict[Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.compressed_frames_array: Dict[Union[None, D2xFrame]] = defaultdict(lambda: None)
        self.missing_blocks: Dict[Union[List[D2xResidualCoordinate], None]] = defaultdict(lambda: None)
        self.residual_blocks: Dict[Union[List[D2xResidualCoordinate], None]] = defaultdict(lambda: None)
        self.residual_images: Dict[Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.residual_images_upscaled: Dict[Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.finished_frames: Dict[Union[D2xFrame, None]] = defaultdict(lambda: None)


if __name__ == "__main__":
    test = D2xManagement()
