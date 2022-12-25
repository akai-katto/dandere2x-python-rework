import os
import shutil
import uuid

import yaml
from pathlib import Path

from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path, get_ffprobe_path, get_a_valid_input_resolution


class Dandere2xSession:

    def __init__(self,
                 session_id: int,
                 input_video_path: Path,
                 workspace: Path,
                 output_path: Path,
                 scale_factor: int,
                 noise_factor: int,
                 block_size: int,
                 quality: float,
                 num_waifu2x_threads: int,
                 output_options: dict):

        # Session Related
        self.session_id = session_id
        self.workspace = workspace

        # Video Related
        self.input_video_path: Path = input_video_path
        self.output_video_path: Path = output_path
        self.block_size: int = block_size
        self.quality: float = quality
        self.scale_factor: int = scale_factor
        self.noise_factor: int = noise_factor
        self.num_waifu2x_threads: int = num_waifu2x_threads

        # Derived Paths
        self.no_sound_video_directory = workspace / "nosound"
        self.no_sound_video_file: Path = self.no_sound_video_directory / ("nosound" + str(uuid.uuid4()) + input_video_path.suffix)
        self.derived_paths = [self.workspace, self.no_sound_video_directory]
        # Dandere2x Config Related
        self.output_options = output_options

        # Video Properties
        self.video_properties = Dandere2xVideoProperties(input_video=input_video_path, block_size=block_size)

    def clear_workspace(self):
        """Clear the contents of the self.workspace directory."""
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)

    def create_paths(self):
        for path in self.derived_paths:
            os.makedirs(path.absolute(), exist_ok=True)

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
