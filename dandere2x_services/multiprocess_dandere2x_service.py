import copy
import glob
import os
import threading
import time
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
        super().__init__(dandere2x_session=dandere2x_session,
                         dandere2x_gui_session_statistics=dandere2x_gui_session_statistics)

        assert is_file_video(ffprobe_dir=self._executable_paths['ffprobe'],
                             input_video=str(self._dandere2x_session.input_video_path.absolute())),\
            "%s is not a video file!" % str(self._dandere2x_session.input_video_path)

        self._child_threads: List[Dandere2x] = []
        self._divided_videos_upscaled: List[str] = []

        self._divided_videos_path = self._dandere2x_session.workspace / "divided_videos"
        self.divided_videos = []

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
        self.divided_videos = sorted(glob.glob(os.path.join(self._divided_videos_path, "*.mkv")))

        # Create unique child_requests for each unique video, with the video being the input.
        for x in range(0, len(self.divided_videos)):
            child_request = Dandere2xSession(session_id=x,
                                             input_video_path=Path(self.divided_videos[x]),
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

    def handle_gui_session_statistics(self):
        if self._dandere2x_gui_session_statistics is not None:

            while True:

                # check to see if all threads are done
                all_done = True
                for thread in self._child_threads:
                    if thread.is_alive():
                        all_done = False

                if all_done:
                    break

                current_frame = 0
                pixels_upscaled_count = 0
                total_pixels_count = 0
                total_frame_count = 0

                for child in self._child_threads:
                    current_frame += child.get_current_frame()
                    pixels_upscaled_count += child.get_upscaled_pixels_count()
                    total_pixels_count += child.get_total_pixels_count()
                    total_frame_count += child.get_frame_count()

                self._dandere2x_gui_session_statistics.current_frame = current_frame
                self._dandere2x_gui_session_statistics.pixels_upscaled_count = pixels_upscaled_count
                self._dandere2x_gui_session_statistics.total_pixels_count = total_pixels_count
                self._dandere2x_gui_session_statistics.frame_count = total_frame_count
                time.sleep(0.01)

            self._dandere2x_gui_session_statistics.is_done = True

    def run(self):
        start_time = time.time()
        self._pre_process()

        for request in self._child_threads:
            request.start()

        threading.Thread(target=self.handle_gui_session_statistics).start()

        for request in self._child_threads:
            request.join()

        self._on_completion()
        duration = time.time() - start_time
        print(f"took {duration} to complete multiprocess")

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

        migrate_tracks_contextless(ffmpeg_dir=ffmpeg_path,
                                   no_audio_file=self._dandere2x_session.no_sound_video_file,
                                   input_file=self._dandere2x_session.input_video_path,
                                   output_file=self._dandere2x_session.output_video_path,
                                   output_options=self._dandere2x_session.output_options)

        for video in self.divided_videos:
            os.remove(video)
