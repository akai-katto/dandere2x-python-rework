import json
import logging
import os
import subprocess


# Credit: https://github.com/k4yt3x/video2x
# Changes: Not much, just got it to work with d2x.
from dandere2xlib.utilities.dandere2x_utils import get_operating_system


def get_video_info(ffprobe_dir, input_video):
    """ Gets input video information
    This method reads input video information
    using ffprobe in dictionary.
    Arguments:
        input_video {string} -- input video file path
    Returns:
        dictionary -- JSON text of input video information
    """

    assert get_operating_system() != "win32" or os.path.exists(ffprobe_dir), "%s does not exist!" % ffprobe_dir

    # this execution command needs to be hard-coded
    # since video2x only strictly recignizes this one format
    execute = [
        ffprobe_dir,
        '-v',
        'panic',
        '-print_format',
        'json',
        '-show_format',
        '-show_streams',
        '-i',
        input_video
    ]
    log = logging.getLogger()
    log.debug("Loading video meta-data with ffprobe.. this might take a while.")
    log.debug("Command: %s" % str(execute))

    json_str = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout

    return json.loads(json_str.decode('utf-8'))


def get_aspect_ratio(ffprobe_dir, input_video):
    """ Gets input video information
    This method reads input video information
    using ffprobe in dictionary.
    Arguments:
        input_video {string} -- input video file path
    Returns:
        dictionary -- JSON text of input video information
    """
    assert get_operating_system() != "win32" or os.path.exists(ffprobe_dir), "%s does not exist!" % ffprobe_dir

    # this execution command needs to be hard-coded
    # since video2x only strictly recignizes this one format
    execute = [
        ffprobe_dir,
        '-v',
        'panic',
        '-select_streams',
        'v:0',
        '-show_entries',
        'stream=display_aspect_ratio',
        '-of',
        'csv=p=0',
        input_video
    ]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_string = return_bytes.decode("utf-8")

    if "N/A" in return_string:
        return None

    return return_string


def get_width_height(ffprobe_dir, input_video):
    """ Gets input video information
    This method reads input video information
    using ffprobe in dictionary.
    Arguments:
        input_video {string} -- input video file path
    Returns:
        dictionary -- JSON text of input video information
    """
    assert get_operating_system() != "win32" or os.path.exists(ffprobe_dir), "%s does not exist!" % ffprobe_dir

    # this execution command needs to be hard-coded
    # since video2x only strictly recignizes this one format
    execute = [
        ffprobe_dir,
        '-v',
        'error',
        '-select_streams',
        'v:0',
        '-show_entries',
        'stream=width,height',
        '-of',
        'csv=p=0',
        input_video
    ]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_string = return_bytes.decode("utf-8").split(",")

    return int(return_string[0]), int(return_string[1])


def get_seconds(ffprobe_dir, input_video) -> float:
    # todo

    execute = [ffprobe_dir,
               "-i", input_video,
               "-show_entries",
               "format=duration",
               "-v", "quiet",
               "-of", "csv=p=0"]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_string = return_bytes.decode("utf-8")

    return float(return_string)


def get_frame_rate(ffprobe_dir, input_video):
    """ Gets input video information
    This method reads input video information
    using ffprobe in dictionary.
    Arguments:
        input_video {string} -- input video file path
    Returns:
        dictionary -- JSON text of input video information
    """
    assert get_operating_system() != "win32" or os.path.exists(ffprobe_dir), "%s does not exist!" % ffprobe_dir

    # this execution command needs to be hard-coded
    # since video2x only strictly recignizes this one format
    execute = [
        ffprobe_dir,
        '-v',
        'error',
        '-select_streams',
        'v:0',
        '-show_entries',
        'stream=avg_frame_rate',
        '-of',
        'csv=p=0',
        input_video
    ]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_string = return_bytes.decode("utf-8")

    return return_string

def is_variable_frame_rate(ffprobe_dir: str, input_video: str) -> bool:

    execute = [ffprobe_dir,
               '-v',
               'quiet',
               '-print_format',
               'json',
               '-show_streams',
               input_video]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_json = json.loads(return_bytes.decode("utf-8"))
    codec_data = {}
    for stream in return_json['streams']:
        if stream['codec_type'] == 'video':
            codec_data = stream

    avg_frame_rate = codec_data['avg_frame_rate']
    num, denom = avg_frame_rate.split("/")
    return denom != "1"

