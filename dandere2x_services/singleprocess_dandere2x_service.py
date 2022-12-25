import os
from abc import ABC
from pathlib import Path

from dandere2x import Dandere2x
from dandere2x_services._dandere2x_service_interface import _Dandere2xServiceInterface
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.ffmpeg_utils import migrate_tracks_contextless


class SingleProcessDandere2xService(_Dandere2xServiceInterface, ABC):

    def __init__(self, dandere2x_session: Dandere2xSession):
        super().__init__(dandere2x_session=dandere2x_session)

    def run(self):
        self._pre_process()
        d2x = Dandere2x(self._dandere2x_session)
        d2x.start()
        d2x.join()
        self._on_completion()

    def _pre_process(self):
        pass

    def _on_completion(self):
        migrate_tracks_contextless(ffmpeg_dir=Path(self._executable_paths['ffmpeg']),
                                   no_audio_file=self._dandere2x_session.no_sound_video_file,
                                   input_file=self._dandere2x_session.input_video_path,
                                   output_file=self._dandere2x_session.output_video_path,
                                   output_options=self._dandere2x_session.output_options,
                                   console_output_dir=None)

        os.remove(self._dandere2x_session.no_sound_video_file)

