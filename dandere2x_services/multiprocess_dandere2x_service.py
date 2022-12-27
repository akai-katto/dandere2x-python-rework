import copy
import glob
import os
from pathlib import Path
from typing import List

from dandere2x import Dandere2x
from dandere2x_services._dandere2x_service_interface import _Dandere2xServiceInterface
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.ffmpeg_utils import divide_video, concat_n_videos, migrate_tracks_contextless, is_file_video
from gui.dandere2_gui_session_statistics import Dandere2xGuiSessionStatistics


class MultiProcessDandere2xService(_Dandere2xServiceInterface):

    def __init__(self,
                 dandere2x_session: Dandere2xSession,
                 dandere2x_gui_session_statistics: Dandere2xGuiSessionStatistics):
        """
        Uses multiple Dandere2xServiceThread to upscale a given file. It does this by attempting to split the video
        up into equal parts, then migrating each upscaled-split video into one complete video file.
        """
        super().__init__(dandere2x_session=copy.copy(dandere2x_session),
                         dandere2x_gui_session_statistics=dandere2x_gui_session_statistics)

        assert is_file_video(ffprobe_dir=self._executable_paths['ffprobe'],
                             input_video=str(self._dandere2x_session.input_video_path.absolute())),\
            "%s is not a video file!" % str(self._dandere2x_session.input_video_path)

        self._child_threads: List[Dandere2x] = []
        self._divided_videos_upscaled: List[str] = []

        self._divided_videos_path = self._dandere2x_session.workspace / "divided_videos"

    def _pre_process(self):
        self._dandere2x_session.clear_workspace()
        self._dandere2x_session.create_paths()

        ffprobe_path = self._executable_paths['ffprobe']
        ffmpeg_path = self._executable_paths['ffmpeg']

        os.makedirs(self._divided_videos_path)

        # Attempt to split the video up into N=3 distinct parts.
        divide_video(ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path,
                     input_video=str(self._dandere2x_session.input_video_path),
                     output_options=self._dandere2x_session.output_options,
                     divide=self._dandere2x_session.output_options['dandere2x']['multiprocess_thread_count'],
                     output_dir=str(self._divided_videos_path.absolute()))

        # Find all the split video files ffmpeg produced in the folder.
        divided_re_encoded_videos = sorted(glob.glob(os.path.join(self._divided_videos_path, "*.mkv")))

        # Create unique child_requests for each unique video, with the video being the input.
        for x in range(0, len(divided_re_encoded_videos)):
            child_request = Dandere2xSession(session_id=x,
                                             input_video_path=Path(divided_re_encoded_videos[x]),
                                             workspace=self._dandere2x_session.workspace / f"subworkspace{x}",
                                             output_path=self._dandere2x_session.output_video_path,
                                             scale_factor=self._dandere2x_session.scale_factor,
                                             noise_factor=self._dandere2x_session.noise_factor,
                                             block_size=self._dandere2x_session.block_size,
                                             quality=self._dandere2x_session.quality,
                                             num_waifu2x_threads=self._dandere2x_session.num_waifu2x_threads,
                                             processing_type="singleprocess",
                                             output_options=self._dandere2x_session.output_options)

            self._divided_videos_upscaled.append(str(child_request.no_sound_video_file))
            self._child_threads.append(Dandere2x(child_request))

    def run(self):
        self._pre_process()

        for request in self._child_threads:
            request.start()

        for request in self._child_threads:
            request.join()

        self._on_completion()

    def _on_completion(self):
        """
        Converts all self._divided_videos_upscaled into one big video, then migrates the original audio into this
        service request's output file.
        """
        ffmpeg_path = self._executable_paths['ffmpeg']
        concat_n_videos(ffmpeg_dir=ffmpeg_path,
                        temp_file_dir=str(self._dandere2x_session.workspace),
                        console_output_dir=str(self._dandere2x_session.workspace),
                        list_of_files=self._divided_videos_upscaled,
                        output_file=str(self._dandere2x_session.no_sound_video_file.absolute()))

        migrate_tracks_contextless(ffmpeg_dir=Path(ffmpeg_path),
                                   no_audio_file=self._dandere2x_session.no_sound_video_file,
                                   input_file=self._dandere2x_session.input_video_path,
                                   output_file=self._dandere2x_session.output_video_path,
                                   output_options=self._dandere2x_session.output_options)
