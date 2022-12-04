import logging
from typing import Tuple

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


def get_a_valid_input_resolution(width: int, height: int, block_size: int) -> Tuple[int, int]:
    width_up = width
    width_down = width

    height_up = height
    height_down = height

    while width_up % block_size != 0:
        width_up = width_up + 1

    while width_down % block_size != 0:
        width_down = width_down - 1

    while height_up % block_size != 0:
        height_up = height_up + 1

    while height_down % block_size != 0:
        height_down = height_down - 1

    smaller_width = width_up if abs(width_up - width) < abs(width_down - width) else width_down

    smaller_height = height_up if abs(height_up - height) < abs(height_down - height) else height_down

    return smaller_width, smaller_height


def check_if_port_is_being_used(port: int):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Try to connect to the given host and port
    if sock.connect_ex(("localhost", port)) == 0:
        sock.close()
        return True
    else:
        sock.close()
        return False
