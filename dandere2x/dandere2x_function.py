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


def dandere2x_function(dandere2x_session: Dandere2xSession):
    set_dandere2x_logger(dandere2x_session.input_video_path.name)

    manager = D2xManagement()
    dandere2x_session = dandere2x_session
    logger = logging.getLogger(dandere2x_session.input_video_path.name)

    frame_extraction = FrameExtraction(manager, dandere2x_session)
    noised_frame_extraction = NoisedFrameExtraction(manager, dandere2x_session)
    frame_compression = FrameCompression(manager, dandere2x_session)
    block_matching = BlockMatching(manager, dandere2x_session)
    residual_processing = ResidualProcessing(manager, dandere2x_session)
    upscale_residuals = UpscaleResiduals(manager, dandere2x_session)
    merge_upscaled_images = MergeUpscaledImages(manager, dandere2x_session)
    pipe_finished_frames_to_video_and_collect_garbage = PipeFinishedFramesToVideoAndCollectGarbage(manager,
                                                                                                         dandere2x_session)

    logger.debug("Starting dandere2x threads")

    frame_extraction.start()
    noised_frame_extraction.start()
    frame_compression.start()
    block_matching.start()
    residual_processing.start()
    upscale_residuals.start()
    merge_upscaled_images.start()
    pipe_finished_frames_to_video_and_collect_garbage.start()

    frame_extraction.join()
    noised_frame_extraction.join()
    frame_compression.join()
    block_matching.join()
    residual_processing.join()
    upscale_residuals.join()
    merge_upscaled_images.join()
    pipe_finished_frames_to_video_and_collect_garbage.join()

    migrate_tracks_contextless(ffmpeg_dir=Path(load_executable_paths_yaml()["ffmpeg"]),
                               no_audio_file=dandere2x_session.no_sound_video_path,
                               input_file=dandere2x_session.input_video_path,
                               output_file=dandere2x_session.output_video_path,
                               output_options=dandere2x_session.output_options,
                               console_output_dir=None)

    os.remove(dandere2x_session.no_sound_video_path)
