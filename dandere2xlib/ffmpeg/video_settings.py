import logging
from fractions import Fraction
from pathlib import Path

from dandere2xlib.ffmpeg.ffmpeg_utils import get_frame_count_ffmpeg
from dandere2xlib.ffmpeg.ffprobe_utils import get_video_info, get_width_height, get_frame_rate, get_aspect_ratio
from dandere2xlib.utilities.dandere2x_utils import get_ffprobe_path, get_ffmpeg_path
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


class VideoSettings:

    def __init__(self, video_file: Path):
        """
        A simple class to get the video settings needed for dandere2x using ffprobe.
        """

        log = logging.getLogger("root")
        self.ffprobe_dir = load_executable_paths_yaml()['ffprobe']
        self.ffmpeg_dir = load_executable_paths_yaml()['ffmpeg']

        self.settings_json = get_video_info(self.ffprobe_dir, video_file)
        self.frame_count = int(get_frame_count_ffmpeg(ffmpeg_dir=self.ffmpeg_dir, input_video=video_file))

        log.debug("setting json %s" % self.settings_json)
        # todo: This entire class can be removed and simplified into the 'except' clause,
        # but having this try / except provides me a sense of security. Some file containers
        # Won't work for the first try, and some won't work for the except, so there's double security here?
        try:
            self.height = self.settings_json['streams'][0]['height']
            self.width = self.settings_json['streams'][0]['width']
            self.frame_rate = float(Fraction(self.settings_json['streams'][0]['avg_frame_rate']))
            self.dar = self.settings_json['streams'][0]['display_aspect_ratio']

        except KeyError:
            log.warning("Warning, getting video information from ffprobe failed. Using backup commands.")
            self.width, self.height = get_width_height(self.ffprobe_dir, video_file)
            self.frame_rate = float(Fraction(get_frame_rate(self.ffprobe_dir, video_file)))
            self.dar = get_aspect_ratio(self.ffprobe_dir, video_file)

        # horizontal videos often do not include rotate so this is separated to keep up the performance
        try:
            self.rotate = int(self.settings_json['streams'][0]["tags"]["rotate"])
        except KeyError:
            self.rotate = int(0)

        log.debug("Loaded Video Settings for %s :" % video_file)
        for item in self.__dict__:
            log.debug("%s : %s" % (item, self.__dict__[item]))

    def log_all_variables(self):
        log = logging.getLogger()

        log.debug("Context Settings:")
        for item in self.__dict__:
            print("%s : %s" % (item, self.__dict__[item]))
