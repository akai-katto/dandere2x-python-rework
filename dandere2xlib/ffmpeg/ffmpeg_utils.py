import logging
import os
import re
import subprocess
import sys
from pathlib import Path

from dandere2xlib.utilities.dandere2x_utils import get_operating_system


def get_frame_count_ffmpeg(ffmpeg_dir: Path, input_video: Path):
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


def migrate_tracks_contextless(ffmpeg_dir: Path, no_audio: str, file_dir: str, output_file: str,
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
                              "-i", no_audio,
                              "-i", file_dir,
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

    migrate_tracks_command.extend([str(output_file)])

    log.info("Migrating tracks %s " % convert(migrate_tracks_command))

    console_output = get_console_output(__name__, console_output_dir)

    log.info("Writing files to %s" % str(console_output_dir))
    log.info("Migrate Command: %s" % convert(migrate_tracks_command))
    subprocess.call(migrate_tracks_command, shell=False, stderr=console_output, stdout=console_output)
    log.info("Finished migrating to file: %s" % output_file)


if __name__ == "__main__":
    test = get_frame_count_ffmpeg(ffmpeg_dir="ffmpeg",
                                  input_video="C:\\Users\\tyler\\Documents\\GitHub\\dandere2x\\src\\workspace\\world_is_mine_cropped.mp4")