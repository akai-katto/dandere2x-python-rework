from dandere2xlib.core.block_matching import BlockMatching
from dandere2xlib.core.frame_compression import FrameCompression
from dandere2xlib.core.frame_extraction import FrameExtraction
from dandere2xlib.core.merge_upscaled_images import MergeUpscaledImages
from dandere2xlib.core.noised_frame_extraction import NoisedFrameExtraction
from dandere2xlib.core.pipe_finished_frames_to_video_and_collect_garbage import \
    PipeFinishedFramesToVideoAndCollectGarbage
from dandere2xlib.core.residual_processing import ResidualProcessing
from dandere2xlib.core.upscale_residuals import UpscaleResiduals
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.d2xsession import Dandere2xSession


class Dandere2x:

    def __init__(self, dandere2x_session: Dandere2xSession):
        manager = D2xManagement()

        self._frame_extraction = FrameExtraction(manager, dandere2x_session)
        self._noised_frame_extraction = NoisedFrameExtraction(manager, dandere2x_session)
        self._frame_compression = FrameCompression(manager, dandere2x_session)
        self._block_matching = BlockMatching(manager, dandere2x_session)
        self._residual_processing = ResidualProcessing(manager, dandere2x_session)
        self._upscale_residuals = UpscaleResiduals(manager, dandere2x_session)
        self._merge_upscaled_images = MergeUpscaledImages(manager, dandere2x_session)
        self._pipe_finished_frames_to_video_and_collect_garbage = PipeFinishedFramesToVideoAndCollectGarbage(manager,
                                                                                                             dandere2x_session)


    def process(self):

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