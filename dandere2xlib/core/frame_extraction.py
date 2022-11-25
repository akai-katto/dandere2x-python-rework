import logging
import time
from pathlib import Path

from threading import Thread
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path, get_wait_delay
from dandere2xlib.ffmpeg.VideoFrameExtractor import VideoFrameExtractor


class FrameExtraction(Thread):

    def __init__(self, manager: D2xManagement, video_path: Path, width: int, height: int):
        super().__init__()
        FFMPEG_PATH = get_ffmpeg_path()

        self.__manager = manager
        self.__extractor = VideoFrameExtractor(ffmpeg_binary=Path(FFMPEG_PATH),
                                               input_video=video_path,
                                               width=width,
                                               height=height)
        self.__loger = logging.getLogger()

    def start(self) -> None:
        block_size = 30
        frame_count = 239

        def part1():
            for pos in range(frame_count):

                while pos > self.__manager.last_upscaled_frame + 60:
                    time.sleep(get_wait_delay())

                frame = self.__extractor.get_frame()
                self.__manager.input_images_array[pos] = frame
                # frame.save(Path(f"inputs\\frame{x}.png"))