import subprocess
from copy import copy
from pathlib import Path

import numpy as np

from dandere2xlib.d2xframe import D2xFrame


class VideoFrameExtractor:

    def __init__(self,
                 ffmpeg_binary: Path,
                 input_video: Path,
                 optional_args,
                 width: int, height: int):

        self.__count: int = 0
        self.__dtype = np.uint8
        self.__height = height
        self.__width = width

        extraction_args = [
            str(ffmpeg_binary), "-vsync", "1", "-loglevel", "panic",
            "-i", str(input_video)
        ]
        extraction_args.extend(optional_args)
        extraction_args.extend(["-c:v", "rawvideo", "-f", "rawvideo",
                                "-pix_fmt", "rgb24", "-an", "-"])

        self.ffmpeg = subprocess.Popen(extraction_args, stdout=subprocess.PIPE)

    @property
    def current_frame(self) -> int:
        return self.__count

    def get_frame(self) -> D2xFrame:
        """Pipes the raw frames to stdout, converts the bytes to NumPy arrays of RGB data.
        This is a generator so usage is (for Frame in self._GetRawFrames(Video))"""

        raw = self.ffmpeg.stdout.read(self.__width * self.__height * 3)
        if not raw:
            raise IndexError(self.__count)

        raw = copy(raw)

        self.__count += 1
        return D2xFrame.from_ndarray(np.frombuffer(raw, dtype=self.__dtype).reshape((self.__height, self.__width, -1)))

