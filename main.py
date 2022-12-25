import logging
import time
from multiprocessing import Process
from pathlib import Path
from threading import Thread

import yaml

from dandere2x import Dandere2x

from dandere2x_services.multiprocess_dandere2x import MultiProcessDandere2x
from dandere2x_services.singleprocess_dandere2x import SingleProcessDandere2x
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import set_dandere2x_logger, log_dandere2x_logo

set_dandere2x_logger(logger_name="root")
logging.propagate = False


def get_session() -> Dandere2xSession:
    """
    :return: A testing version of dandere2x session.
    """

    with open("./config_files/output_options.yaml") as f:
        output_options = yaml.safe_load(f)

    return Dandere2xSession(session_id=0,
                            input_video_path=Path("workspace/2sec.mkv"),
                            workspace=Path("workspace/workingspace"),
                            output_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\pp_test.mkv"),
                            scale_factor=2,
                            noise_factor=3,
                            block_size=30,
                            quality=100,
                            num_waifu2x_threads=4,
                            output_options=output_options)


if __name__ == "__main__":
    start = time.time()

    session0 = get_session()
    mpd2x0 = MultiProcessDandere2x(session0)
    mpd2x0.start()
    mpd2x0.join()

    print(f"end: {time.time() - start}")
