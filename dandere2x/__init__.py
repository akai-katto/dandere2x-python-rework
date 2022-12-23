import logging
import os
from pathlib import Path
from threading import Thread

from dandere2x.block_matching import BlockMatching
from dandere2x.frame_compression import FrameCompression
from dandere2x.frame_extraction import FrameExtraction
from dandere2x.merge_upscaled_images import MergeUpscaledImages
from dandere2x.noised_frame_extraction import NoisedFrameExtraction
from dandere2x.pipe_finished_frames_to_video_and_collect_garbage import \
    PipeFinishedFramesToVideoAndCollectGarbage
from dandere2x.residual_processing import ResidualProcessing
from dandere2x.upscale_residuals import UpscaleResiduals
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.ffmpeg_utils import migrate_tracks_contextless
from dandere2xlib.utilities.dandere2x_utils import set_dandere2x_logger
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


class Dandere2x(Thread):

    def __init__(self, dandere2x_session: Dandere2xSession):
        super().__init__(name=f"session {dandere2x_session.session_id}")
        set_dandere2x_logger(dandere2x_session.input_video_path.name)

        manager = D2xManagement()
        self.dandere2x_session = dandere2x_session
        self.__logger = logging.getLogger(dandere2x_session.input_video_path.name)

        self._frame_extraction = FrameExtraction(manager, dandere2x_session)
        self._noised_frame_extraction = NoisedFrameExtraction(manager, dandere2x_session)
        self._frame_compression = FrameCompression(manager, dandere2x_session)
        self._block_matching = BlockMatching(manager, dandere2x_session)
        self._residual_processing = ResidualProcessing(manager, dandere2x_session)
        self._upscale_residuals = UpscaleResiduals(manager, dandere2x_session)
        self._merge_upscaled_images = MergeUpscaledImages(manager, dandere2x_session)
        self._pipe_finished_frames_to_video_and_collect_garbage = PipeFinishedFramesToVideoAndCollectGarbage(manager,
                                                                                                             dandere2x_session)

    def run(self):
        self.__logger.debug("Starting dandere2x threads")

        self._frame_extraction.start()
        self._noised_frame_extraction.start()
        self._frame_compression.start()
        self._block_matching.start()
        self._residual_processing.start()
        self._upscale_residuals.start()
        self._merge_upscaled_images.start()
        self._pipe_finished_frames_to_video_and_collect_garbage.start()

        self._frame_extraction.join()
        self._noised_frame_extraction.join()
        self._frame_compression.join()
        self._block_matching.join()
        self._residual_processing.join()
        self._upscale_residuals.join()
        self._merge_upscaled_images.join()
        self._pipe_finished_frames_to_video_and_collect_garbage.join()

        migrate_tracks_contextless(ffmpeg_dir=Path(load_executable_paths_yaml()["ffmpeg"]),
                                   no_audio_file=self.dandere2x_session.no_sound_video_path,
                                   input_file=self.dandere2x_session.input_video_path,
                                   output_file=self.dandere2x_session.output_video_path,
                                   output_options=self.dandere2x_session.output_options,
                                   console_output_dir=None)

        os.remove(self.dandere2x_session.no_sound_video_path)
