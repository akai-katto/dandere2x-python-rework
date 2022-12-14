import os
import threading
import time
from abc import ABC
from pathlib import Path

from dandere2x import Dandere2x
from dandere2x_services._dandere2x_service_interface import _Dandere2xServiceInterface
from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.d2x_suspend_management import Dandere2xSuspendManagement
from dandere2xlib.ffmpeg.ffmpeg_utils import migrate_tracks_contextless
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from gui.dandere2_gui_session_statistics import Dandere2xGuiSessionStatistics


class SingleProcessDandere2xService(_Dandere2xServiceInterface, ABC):

    def __init__(self,
                 dandere2x_session: Dandere2xSession,
                 dandere2x_gui_session_statistics: Dandere2xGuiSessionStatistics,
                 dandere2x_suspend_management: Dandere2xSuspendManagement):
        super().__init__(dandere2x_session=dandere2x_session,
                         dandere2x_gui_session_statistics=dandere2x_gui_session_statistics,
                         dandere2x_suspend_management=dandere2x_suspend_management)

        self.d2x: Dandere2x = None

    def run(self):
        self._pre_process()
        self.d2x = Dandere2x(self._dandere2x_session, self._dandere2x_suspend_management)
        self.d2x.start()
        threading.Thread(target=self.handle_gui_session_statistics).start()
        self.d2x.join()
        self._on_completion()

    def handle_gui_session_statistics(self):
        if self._dandere2x_gui_session_statistics is not None:
            self._dandere2x_gui_session_statistics.frame_count = self.d2x.get_frame_count()

            while self.d2x.is_alive():
                self._dandere2x_gui_session_statistics.current_frame = self.d2x.get_current_frame()
                self._dandere2x_gui_session_statistics.pixels_upscaled_count = self.d2x.get_upscaled_pixels_count()
                self._dandere2x_gui_session_statistics.total_pixels_count = self.d2x.get_total_pixels_count()
                time.sleep(0.01)

            self._dandere2x_gui_session_statistics.is_done = True

    def _pre_process(self):
        pass

    def _on_completion(self):
        migrate_tracks_contextless(ffmpeg_dir=self._executable_paths['ffmpeg'],
                                   no_audio_file=self._dandere2x_session.no_sound_video_file,
                                   input_file=self._dandere2x_session.input_video_path,
                                   output_file=self._dandere2x_session.output_video_path,
                                   output_options=self._dandere2x_session.output_options,
                                   console_output_dir=None)

        os.remove(self._dandere2x_session.no_sound_video_file)

