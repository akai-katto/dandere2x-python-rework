import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import List

from dandere2xlib.d2xsession.__init__ import Dandere2xSession
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.utilities.dandere2x_utils import get_ffmpeg_path
from dandere2xlib.utilities.yaml_utils import get_options_from_section


class FramesToVideoPipe(threading.Thread):
    """
    The pipe class allows images (Frame.py) to be processed into a video directly. It does this by "piping"
    images to ffmpeg, thus removing the need for storing the processed images onto the disk.
    """

    def __init__(self,
                 output_video: Path,
                 dandere2x_session: Dandere2xSession):
        threading.Thread.__init__(self, name="frames to video pipe")
        self.log = logging.getLogger()

        self.dandere2x_session = dandere2x_session
        self.output_video: Path = output_video

        # class specific
        self.ffmpeg_pipe_subprocess = None
        self.alive: bool = False
        self.images_to_pipe: List[D2xFrame] = []
        self.buffer_limit: int = 20

    def kill(self) -> None:
        self.log.info("Kill called.")
        self.alive = False

    def run(self) -> None:
        self.log.info("Run Called")

        self.alive = True
        self._setup_pipe()

        # keep piping images to ffmpeg while this thread is supposed to be kept alive.
        while self.alive:
            if len(self.images_to_pipe) > 0:
                img = self.images_to_pipe.pop(0).get_pil_image()  # get the first image and remove it from list
                img.save(self.ffmpeg_pipe_subprocess.stdin, format="jpeg", quality=100)
            else:
                time.sleep(0.01)

        self.ffmpeg_pipe_subprocess.stdin.close()
        self.ffmpeg_pipe_subprocess.wait()

        # ensure thread is dead (can be killed with controller.kill() )
        self.alive = False

    # todo: Implement this without a 'while true'
    def save(self, frame):
        """
        Try to add an image to image_to_pipe buffer. If there's too many images in the buffer,
        simply wait until the buffer clears.
        """
        while True:
            if len(self.images_to_pipe) < self.buffer_limit:
                self.images_to_pipe.append(frame)
                break
            time.sleep(0.05)

    def _setup_pipe(self) -> None:
        self.log.info("Setting up pipe Called")

        # load variables..
        ffmpeg_dir = get_ffmpeg_path()

        # constructing the pipe command...
        ffmpeg_pipe_command = [ffmpeg_dir]

        hw_accel = self.dandere2x_session.output_options["ffmpeg"]["pipe_video"]["-hwaccel"]
        if hw_accel is not None:
            ffmpeg_pipe_command.append("-hwaccel")
            ffmpeg_pipe_command.append(hw_accel)

        ffmpeg_pipe_command.extend(["-r", str(self.dandere2x_session.video_properties.input_video_settings.frame_rate)])

        options = get_options_from_section(self.dandere2x_session.output_options["ffmpeg"]["pipe_video"]['output_options'],
                                           ffmpeg_command=True)

        ffmpeg_pipe_command.extend(options)

        ffmpeg_pipe_command.append(str(self.output_video.absolute()))

        # # Starting the Pipe Command
        # console_output = open(self.context.console_output_dir + "pipe_output.txt", "w")
        # console_output.write(str(ffmpeg_pipe_command))

        self.log.info("ffmpeg_pipe_command %s" % str(ffmpeg_pipe_command))
        self.ffmpeg_pipe_subprocess = subprocess.Popen(ffmpeg_pipe_command,
                                                       stdin=subprocess.PIPE)
