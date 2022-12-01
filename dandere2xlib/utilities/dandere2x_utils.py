import logging

import colorlog
from pathlib import Path
from platform import platform



def get_ffmpeg_path() -> Path:
    # temporary, to replace later
    return Path("C:\\ffmpeg\\ffmpeg.exe")

def get_ffprobe_path() -> Path:
    # temporary, to replace later
    return Path("C:\\ffmpeg\\ffprobe.exe")

def get_wait_delay() -> float:
    return 0.001


def get_operating_system():
    if platform == "linux" or platform == "linux2" or platform == "darwin":  # macos is pretty indistinguishable
        return 'linux'
    elif platform == "win32":
        return 'win32'

def set_dandere2x_logger(input_file_path: str) -> None:
    """
    Create the logging class to be format print statements the dandere2x way.

    The formatted output resembles the following (roughly):
        outputvid0.mkv 2020-08-01 16:03:39,455 INFO     __init__.py : Hewwooo
        outputvid0.mkv 2020-08-01 16:03:39,456 WARNING  __init__.py : jeeez fuck this warning
        outputvid0.mkv 2020-08-01 16:03:39,456 ERROR    __init__.py : oh fuck fuck fuck stop the program an error occurred
    """
    input_file_name = Path(input_file_path).name + " "
    color_log_format = input_file_name + "%(log_color)s%(asctime)-8s%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(filename)-8s%(reset)s %(log_color)s%(funcName)-8s%(reset)s: %(log_color)s%(message)s"

    formatter = colorlog.ColoredFormatter(
        color_log_format,
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)

    logger = colorlog.getLogger(name=input_file_path)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("Dandere2x Console Logger Set")