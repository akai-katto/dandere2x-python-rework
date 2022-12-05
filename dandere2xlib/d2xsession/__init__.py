import yaml
from pathlib import Path

from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path, get_ffprobe_path, get_a_valid_input_resolution


class Dandere2xSession:

    def __init__(self,
                 input_video_path: Path,
                 output_path: Path,
                 scale_factor: int,
                 noise_factor: int,
                 block_size: int,
                 quality: float,
                 num_waifu2x_threads: int,
                 output_options: dict):

        # Video Related
        self.input_video_path: Path = input_video_path
        self.no_sound_video_path: Path = input_video_path.parent / ("nosound" + input_video_path.suffix)
        self.output_video_path: Path = output_path
        self.block_size: int = block_size
        self.quality: float = quality
        self.scale_factor: int = scale_factor
        self.noise_factor: int = noise_factor
        self.num_waifu2x_threads: int = num_waifu2x_threads

        # Dandere2x Config Related
        self.output_options = output_options

        # Video Properties
        self.video_properties = Dandere2xVideoProperties(input_video=input_video_path, block_size=block_size)

class Dandere2xVideoProperties:

    def __init__(self, input_video: Path, block_size: int):
        self.input_video = input_video
        self.block_size = block_size

        self.input_video_settings = VideoSettings(input_video)

        # We need to resize the input video in order for block matching to work.
        self.corrected_video_width, self.corrected_video_height = \
            get_a_valid_input_resolution(self.input_video_settings.width,
                                         self.input_video_settings.height,
                                         self.block_size)
