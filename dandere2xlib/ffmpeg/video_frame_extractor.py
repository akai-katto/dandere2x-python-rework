import subprocess
from copy import copy
from pathlib import Path

import numpy as np

from dandere2xlib.d2xsession.__init__ import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.utilities.yaml_utils import get_options_from_section


class VideoFrameExtractor:

    def __init__(self,
                 ffmpeg_binary: Path,
                 input_video: Path,
                 width: int,
                 height: int,
                 dandere2x_session: Dandere2xSession,
                 optional_args=[]
                 ):

        self.dandere2x_session = dandere2x_session

        self.__count: int = 0
        self.__dtype = np.uint8
        self.__height = height
        self.__width = width

        # We apply vsync since we apply vsync for counting frames, as well as keeping the frame rate consistent.
        extraction_args = [
            str(ffmpeg_binary), "-vsync", "1", "-loglevel", "panic",
            "-i", str(input_video)
        ]

        options = get_options_from_section(
            self.dandere2x_session.output_options["ffmpeg"]["pre_process_video"]['output_options'],
            ffmpeg_command=True)
        for item in options:
            extraction_args.append(item)

        extraction_args.extend(optional_args)

        extraction_args.extend(["-s", f"{self.__width}:{self.__height}"])  # Force the resolution to match
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
