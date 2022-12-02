import yaml
from pathlib import Path

from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path, get_ffprobe_path


class Dandere2xSession:

    def __init__(self,
                 video_path: Path,
                 scale_factor: int,
                 block_size: int,
                 quality: float,
                 output_options: dict,
                 executable_paths: dict):

        # Video Related
        self.video_path: Path = video_path
        self.block_size: int = block_size
        self.quality: float = quality
        self.scale_factor: int = scale_factor

        # Dandere2x Config Related
        self.output_options = output_options
        self.executable_paths = executable_paths

        # Video Properties
        self.video_properties = Dandere2xVideoProperties(input_video=video_path, block_size=block_size)


def get_dandere2x_session() -> Dandere2xSession:
    """
    :return: A testing version of dandere2x session.
    """

    with open("./config_files/output_options.yaml") as f:
        output_options = yaml.safe_load(f)

    with open("./config_files/executable_paths.yaml") as f:
        executable_paths = yaml.safe_load(f)

    return Dandere2xSession(video_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\yn_small.mkv"),
                            scale_factor=2,
                            block_size=20,
                            quality=10,
                            output_options=output_options,
                            executable_paths=executable_paths)


class Dandere2xVideoProperties:

    def __init__(self, input_video: Path, block_size: int):

        self.input_video = input_video
        self.block_size = block_size

        self.input_video_settings = VideoSettings(input_video)

        # We need to resize the input video in order for block matching to work.
        self.corrected_video_width = self.input_video_settings.width
        self.corrected_video_height = self.input_video_settings.height
        


