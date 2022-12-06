import logging
import time
from pathlib import Path

import yaml

from logging import getLogger
from dandere2xlib.core import Dandere2x
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import set_dandere2x_logger, log_dandere2x_logo, get_operating_system

set_dandere2x_logger(logger_name="root")
logging.propagate = False


def get_dandere2x_session() -> Dandere2xSession:
    """
    :return: A testing version of dandere2x session.
    """

    with open("./config_files/output_options.yaml") as f:
        output_options = yaml.safe_load(f)

    with open("./config_files/executable_paths.yaml") as f:
        executable_paths = yaml.safe_load(f)

    return Dandere2xSession(input_video_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\short_steal.mkv"),
                            output_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\short_steal2x.mkv"),
                            scale_factor=2,
                            noise_factor=3,
                            block_size=30,
                            quality=80,
                            num_waifu2x_threads=3,
                            output_options=output_options)


def user_generate_dandere2x_session() -> Dandere2xSession:
    """
    :return: A testing version of dandere2x session.
    """
    log_dandere2x_logo("root")
    log = logging.getLogger("root")

    with open("./config_files/output_options.yaml") as f:
        output_options = yaml.safe_load(f)

    with open("./config_files/executable_paths.yaml") as f:
        executable_paths = yaml.safe_load(f)

    log.info("Starting Dandere2x Session Builder... ")
    log.info("This is an interactive session and requires user input to function.")
    log.info("You will be asked to provide details regarding your upscale request.")
    log.info("")
    log.info("")

    log.info('---INPUT VIDEO PATH ---')
    log.info("Type in the path to your input video")
    video_path = Path(input())

    is_video = False
    while not is_video:
        try:
            video_settings = VideoSettings(video_path)
            is_video = True
            log.info(f"{video_path.name} is a valid video. Continuing.")
        except Exception as e:
            log.error("Error, the file you selected is not a valid video. Please input another file,"
                      "or try again.")
            log.error(f"Raised exception: {e}")
            video_path = Path(input())

    log.info("Enter your output video path. Please ensure the directory exists.")
    output_path = Path(input())
    log.info(f"Your output path is {str(output_path)}")

    log.info("Input your scale factor. Valid inputs are 2, 4, 8")
    scale_factor = int(input())
    while scale_factor not in [2, 4, 8]:
        log.error("Invalid scale factor. Try again")
        scale_factor = int(input())

    log.info("Input your noise factor. Valid inputs are 0,1,2,3")
    noise_factor = int(input())
    while noise_factor not in [0, 1, 2, 3]:
        log.error("Invalid noise factor. Try again")
        noise_factor = int(input())

    log.info("Input your block size. Recommended blocksizes are [20,30,60]. ")
    block_size = int(input())

    log.info("Input your quality ratio. Ranges are [0-100]. Recommended is 80+")
    quality = int(input())
    while quality not in range(0, 101):  # [0-100]
        log.error("Invalid quality factor. Try again")
        quality = int(input())

    log.info("Input the number of waifu2x-ncnn-vulkan instances to use. Recommended 2. Maximum 4.")
    num_waifu2x_threads = int(input())
    while num_waifu2x_threads not in range(0, 5):  # [0-100]
        log.error("Invalid quality factor. Try again")
        num_waifu2x_threads = int(input())

    return Dandere2xSession(input_video_path=video_path,
                            output_path=output_path,
                            scale_factor=scale_factor,
                            noise_factor=noise_factor,
                            block_size=block_size,
                            quality=quality,
                            num_waifu2x_threads=num_waifu2x_threads,
                            output_options=output_options)


if __name__ == "__main__":

    dandere2x_session = get_dandere2x_session()
    start = time.time()
    d2x = Dandere2x(dandere2x_session)
    d2x.process()
    print(f"end: {time.time() - start}")
