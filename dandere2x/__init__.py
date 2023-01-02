import logging
from threading import Thread

from dandere2x.block_matching import BlockMatching
from dandere2x.frame_compression import FrameCompression
from dandere2x.frame_extraction import FrameExtraction
from dandere2x.merge_upscaled_images import MergeUpscaledImages
from dandere2x.noised_frame_extraction import NoisedFrameExtraction
from dandere2x.pipe_finished_frames_to_video_and_collect_garbage import PipeFinishedFramesToVideoAndCollectGarbage
from dandere2x.residual_processing import ResidualProcessing
from dandere2x.upscale_residuals import UpscaleResiduals

from dandere2xlib.d2x_suspend_management import Dandere2xSuspendManagement
from dandere2xlib.d2x_management import D2xManagement
from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.utilities.dandere2x_utils import set_dandere2x_logger


class Dandere2x(Thread):

    def __init__(self,
                 dandere2x_session: Dandere2xSession,
                 dandere2x_suspend_management: Dandere2xSuspendManagement):
        super().__init__(name=f"session {dandere2x_session.session_id}")
        set_dandere2x_logger(dandere2x_session.input_video_path.name)

        self._manager = D2xManagement()
        self._dandere2x_session = dandere2x_session
        self.__logger = logging.getLogger(dandere2x_session.input_video_path.name)

        self._frame_extraction = FrameExtraction(self._manager, dandere2x_session)
        self._noised_frame_extraction = NoisedFrameExtraction(self._manager, dandere2x_session)
        self._frame_compression = FrameCompression(self._manager, dandere2x_session)
        self._block_matching = BlockMatching(self._manager, dandere2x_session)
        self._residual_processing = ResidualProcessing(self._manager, dandere2x_session)
        self._upscale_residuals = UpscaleResiduals(self._manager, dandere2x_session, dandere2x_suspend_management)
        self._merge_upscaled_images = MergeUpscaledImages(self._manager, dandere2x_session)
        self._pipe_finished_frames_to_video_and_collect_garbage =\
            PipeFinishedFramesToVideoAndCollectGarbage(self._manager, dandere2x_session, dandere2x_suspend_management)

    def run(self):
        self._dandere2x_session.clear_workspace()
        self._dandere2x_session.create_paths()

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

    # Metadata accessors

    def get_upscaled_pixels_count(self):
        return self._residual_processing.pixels_upscaled_count

    def get_total_pixels_count(self):
        return self._residual_processing.total_pixels_count

    def get_frame_count(self):
        return self._dandere2x_session.video_properties.input_video_settings.frame_count

    def get_current_frame(self):
        return self._manager.last_piped_frame
