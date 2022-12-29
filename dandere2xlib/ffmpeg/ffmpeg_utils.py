import logging
import os
import re
import subprocess
import sys
from pathlib import Path

from dandere2xlib.ffmpeg.ffprobe_utils import get_seconds
from dandere2xlib.utilities.dandere2x_utils import get_operating_system
from dandere2xlib.utilities.yaml_utils import get_options_from_section


def get_console_output(method_name: str, console_output_dir=None):
    if console_output_dir:
        assert type(console_output_dir) == str

        log_file = os.path.join(console_output_dir, method_name + "output.txt")
        console_output = open(log_file, "w", encoding="utf8")
        return console_output

    return open(os.devnull, 'w')


def get_frame_count_ffmpeg(ffmpeg_dir: str, input_video: Path):
    assert get_operating_system() != "win32" or os.path.exists(ffmpeg_dir), "%s does not exist!" % ffmpeg_dir

    # We apply vsync since we apply vsync for counting frames, as well as keeping the frame rate consistent.
    # See video_frame_extractor.py
    execute = [
        ffmpeg_dir,
        "-vsync", str(1),
        "-i", str(input_video.absolute()),
        "-c", "copy",
        "-f", "null",
        "-"
    ]

    process = subprocess.run(execute, capture_output=True)
    stdout_as_str = process.stderr.decode("utf-8")

    regex = re.compile("frame=.{0,3}[0-9]{1,10}")
    matched_regex = regex.findall(stdout_as_str)
    assert matched_regex

    matched_regex = matched_regex[-1]
    frame_count = re.compile("\d{1,10}").findall(matched_regex)[0]
    return int(frame_count)


def concat_n_videos(ffmpeg_dir: str,
                    temp_file_dir: str,
                    list_of_files: list,
                    output_file: str,
                    console_output_dir=None) -> None:
    import subprocess

    file_list_text_file = os.path.join(temp_file_dir, "temp.txt")

    file_template = "file " + "'" + "%s" + "'" + "\n"

    # we need to create a text file for ffmpeg's concat function to work properly.
    file = open(file_list_text_file, "w+")
    for file_name in list_of_files:
        file.write(file_template % file_name)
    file.close()

    concat_videos_command = [ffmpeg_dir,
                             "-f", "concat",
                             "-safe", "0",
                             "-i", file_list_text_file]

    concat_videos_command.extend([output_file])

    console_output = get_console_output(__name__, console_output_dir)
    subprocess.call(concat_videos_command, shell=False, stderr=console_output, stdout=console_output)


def migrate_tracks_contextless(ffmpeg_dir: str,
                               no_audio_file: Path,
                               input_file: Path,
                               output_file: Path,
                               output_options: dict,
                               console_output_dir=None):
    """
    Add the audio tracks from the original video to the output video.
    """

    log = logging.getLogger("root")

    # to remove
    def convert(lst):
        return ' '.join(lst)

    log = logging.getLogger()

    migrate_tracks_command = [ffmpeg_dir,
                              "-i", str(no_audio_file.absolute()),
                              "-i", str(input_file.absolute()),
                              "-map", "0:v?",
                              "-map", "1:a?",
                              "-map", "1:s?",
                              "-map", "1:d?",
                              "-map", "1:t?"
                              ]

    options = get_options_from_section(output_options["ffmpeg"]['migrate_audio']['output_options'],
                                       ffmpeg_command=True)
    for element in options:
        migrate_tracks_command.append(element)

    migrate_tracks_command.extend([str(output_file.absolute())])

    log.info("Migrating tracks %s " % convert(migrate_tracks_command))

    console_output = get_console_output(__name__, console_output_dir)

    log.info("Writing files to %s" % str(console_output_dir))
    log.info("Migrate Command: %s" % convert(migrate_tracks_command))
    subprocess.call(migrate_tracks_command, shell=False, stderr=console_output, stdout=console_output)
    log.info("Finished migrating to file: %s" % output_file)


def divide_video(ffmpeg_path: str,
                 ffprobe_path: str,
                 input_video: str,
                 output_options: dict,
                 divide: int,
                 output_dir: str):
    """

    Attempts to divide a video into N different segments, using the ffmpeg segment_time argument. See the reading
    I referenced here: 
        https://superuser.com/questions/692714/how-to-split-videos-with-ffmpeg-and-segment-times-option

    Note that this will not perfectly divide the video into N different, equally sized chunks, but rather will cut them
    where keyframes allow them to be split. 

    Args:
        ffmpeg_path: ffmpeg binary
        ffprobe_path: ffprobe binary
        input_video: File to be split
        output_options: Dictionary containing the loaded ./config_files/output_options.yaml
        divide: N divisions.
        output_dir: Where to save split_video%d.mkv's. 

    Returns:
        Nothing, but split_video%d.mkv files will appear in output_dir.
    """
    import math

    seconds = int(get_seconds(ffprobe_dir=ffprobe_path, input_video=input_video))
    ratio = math.ceil(seconds / divide)
    execute = [ffmpeg_path]

    hw_accel = output_options["ffmpeg"]["divide_video"]["-hwaccel"]
    if hw_accel is not None:
        execute.append("-hwaccel")
        execute.append(hw_accel)

    execute.extend(["-i", input_video,
                    "-f", "segment",
                    "-segment_time", str(ratio),
                    "-c", "copy"])

    execute.append(os.path.join(output_dir, "split_video%d.mkv"))

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout
    return_string = return_bytes.decode("utf-8")

    return return_string


def is_file_video(ffprobe_dir: str,
                  input_video: str):
    assert get_operating_system() != "win32" or os.path.exists(ffprobe_dir), "%s does not exist!" % ffprobe_dir

    execute = [
        ffprobe_dir,
        "-i", input_video,
        "-v", "quiet"
    ]

    return_bytes = subprocess.run(execute, check=True, stdout=subprocess.PIPE).stdout

    if "Invalid data found when processing input" in return_bytes.decode("utf-8"):
        return False

    return True


if __name__ == "__main__":
    test = get_frame_count_ffmpeg(ffmpeg_dir="ffmpeg",
                                  input_video="C:\\Users\\tyler\\Documents\\GitHub\\dandere2x\\src\\workspace\\world_is_mine_cropped.mp4")
