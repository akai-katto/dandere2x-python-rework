import sys

from typing import Mapping, Set, Union, List, Dict
from collections import defaultdict
from dandere2xlib.d2x_frame import D2xFrame
from dandere2xlib.models.d2x_residual_coordinate import D2xResidualCoordinate


class D2xManagement:

    def __init__(self):
        self.last_piped_frame = 0

        self.input_images_array: Dict[int, Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.noised_images_array: Dict[int, Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.compressed_frames_array: Dict[int, Union[None, D2xFrame]] = defaultdict(lambda: None)
        self.missing_blocks: Dict[int, Union[List[D2xResidualCoordinate], None]] = defaultdict(lambda: None)
        self.residual_blocks: Dict[int, Union[List[D2xResidualCoordinate], None]] = defaultdict(lambda: None)
        self.residual_images: Dict[int, Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.residual_images_upscaled: Dict[int, Union[D2xFrame, None]] = defaultdict(lambda: None)
        self.finished_frames: Dict[int, Union[D2xFrame, None]] = defaultdict(lambda: None)


if __name__ == "__main__":
    test = D2xManagement()
