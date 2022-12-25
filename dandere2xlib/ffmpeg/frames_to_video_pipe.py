import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import List

from dandere2xlib.d2xsession.__init__ import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path
from dandere2xlib.utilities.yaml_utils import get_options_from_section, load_executable_paths_yaml
from dandere2xlib.ffmpeg.ffmpeg_utils import concat_n_videos

class FramesToVideoPipe(threading.Thread):
    """
    The pipe class allows images (Frame.py) to be processed into a video directly. It does this by "piping"
    images to ffmpeg, thus removing the need for storing the processed images onto the disk.
    """

    def __init__(self,
                 output_video: Path,
                 dandere2x_session: Dandere2xSession):
        threading.Thread.__init__(self, name="frames to video pipe")
        self._log = logging.getLogger(dandere2x_session.input_video_path.name)

        self._dandere2x_session = dandere2x_session
        self._PIPE_VIDEOS_MAX_FRAMES = self._dandere2x_session.output_options['dandere2x']['pipe_video_max_frames']
        self._output_video: Path = output_video
        self._FFMPEG_PATH = load_executable_paths_yaml()["ffmpeg"]

        # class specific
        self.ffmpeg_pipe_subprocess = None
        self.alive: bool = False
        self.images_to_pipe: List[D2xFrame] = []
        self.__buffer_limit: int = 20

        self.__list_of_videos: List[str] = []

    def kill(self) -> None:
        self._log.info("Kill called.")
        self.alive = False

    def run(self) -> None:
        self._log.info("Run Called")

        self.alive = True
        self._setup_pipe(0)

        current_video = 0
        piped_frames_in_video = 0

        # keep piping images to ffmpeg while this thread is supposed to be kept alive.
        while self.alive:

            if len(self.images_to_pipe) > 0:

                piped_frames_in_video += 1
                if piped_frames_in_video > self._PIPE_VIDEOS_MAX_FRAMES:
                    current_video += 1
                    piped_frames_in_video = 0

                    self.ffmpeg_pipe_subprocess.stdin.close()
                    self.ffmpeg_pipe_subprocess.wait()
                    self._setup_pipe(current_video)
                img = self.images_to_pipe.pop(0).get_pil_image()  # get the first image and remove it from list
                img.save(self.ffmpeg_pipe_subprocess.stdin, format="BMP")
            else:
                time.sleep(0.001)

        self.ffmpeg_pipe_subprocess.stdin.close()
        self.ffmpeg_pipe_subprocess.wait()

        concat_n_videos(ffmpeg_dir=self._FFMPEG_PATH,
                        temp_file_dir=str(self._output_video.parent),
                        list_of_files=self.__list_of_videos,
                        output_file=str(self._output_video))

        for partial_video in self.__list_of_videos:
            os.remove(partial_video)


    # todo: Implement this without a 'while true'
    def save(self, frame):
        """
        Try to add an image to image_to_pipe buffer. If there's too many images in the buffer,
        simply wait until the buffer clears.
        """
        while True:
            if len(self.images_to_pipe) < self.__buffer_limit:
                self.images_to_pipe.append(frame)
                break
            time.sleep(0.05)

    def _setup_pipe(self, extension: int) -> None:
        self._log.info("Setting up pipe Called")

        output_file = self._output_video.parent /\
                      f"{self._output_video.name.removesuffix(self._output_video.suffix)}_{extension}{self._output_video.suffix}"

        # constructing the pipe command...
        ffmpeg_pipe_command = [self._FFMPEG_PATH]

        hw_accel = self._dandere2x_session.output_options["ffmpeg"]["pipe_video"]["-hwaccel"]
        if hw_accel is not None:
            ffmpeg_pipe_command.append("-hwaccel")
            ffmpeg_pipe_command.append(hw_accel)

        ffmpeg_pipe_command.extend(["-r", str(self._dandere2x_session.video_properties.input_video_settings.frame_rate)])
        ffmpeg_pipe_command.extend(["-pix_fmt", self._dandere2x_session.video_properties.input_video_settings.pix_fmt])

        options = get_options_from_section(self._dandere2x_session.output_options["ffmpeg"]["pipe_video"]['output_options'],
                                           ffmpeg_command=True)

        ffmpeg_pipe_command.extend(options)
        ffmpeg_pipe_command.append(str(output_file.absolute()))

        # # Starting the Pipe Command
        # console_output = open(self.context.console_output_dir + "pipe_output.txt", "w")
        # console_output.write(str(ffmpeg_pipe_command))

        self.__list_of_videos.append(str(output_file.absolute()))
        self._log.info("ffmpeg_pipe_command %s" % str(ffmpeg_pipe_command))
        self.ffmpeg_pipe_subprocess = subprocess.Popen(ffmpeg_pipe_command,
                                                       stdin=subprocess.PIPE)
