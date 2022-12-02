import os
from pathlib import Path
import yaml

from dandere2xlib.utilities.dandere2x_utils import get_operating_system


def load_executable_paths_yaml() -> dict:
    """
    Load the dandere2x_directories yaml file, but replace all the relative path definitions with absolute
    definitions.
    """
    from os import path
    import logging
    from pathlib import Path
    import sys

    logger = logging.getLogger()

    # For some reason, detecting if python is frozen or not isn't working on pyinstaller (on my machine, at least).
    # This will cycle through the two options, if we're running as a python script, or if we're running as an
    # executable, and return whatever one works. I wish the frozen thing worked on my system
    potential_main_paths = [os.path.dirname(os.path.abspath(sys.executable)), Path(path.abspath(sys.modules['__main__'].__file__)).parent]

    # This is acquired technical debt / my pyinstaller refuses to work by simply checking if it's frozen.
    for potential in potential_main_paths:
        # get location of dandere2x directories (will be in the same folder as main)
        configfile = "executable_paths.yaml"
        main_path = potential
        config_path = Path(path.join(main_path, "config_files"))
        directory_file = os.path.join(config_path, configfile)

        try:
            # load yaml
            with open(directory_file, "r") as read_file:
                config = yaml.safe_load(read_file)
                logger.info(f"Main path {potential} loaded {configfile} successfully. ")
                break
        except:
            logger.info(f"main_path option {potential} did not work, trying the next main_path option")

    # replace each relative path with it's absolute counter-part (if applicable)
    for key in config:

        # use system binaries if on linux for ffmpeg / ffprobe
        if key == "ffmpeg" and get_operating_system() == "linux":
            config[key] = "ffmpeg"
            continue

        if key == "ffprobe" and get_operating_system() == "linux":
            config[key] = "ffprobe"
            continue

        if get_operating_system() == "win32":
            """ Modifications needed to take place if we're not unix-based """
            config[key] = config[key].replace("/", "\\")
            config[key] = config[key] + ".exe"

        if not os.path.isabs(config[key]):
            config[key] = os.path.join(main_path, config[key])

    return config


def get_options_from_section(section: yaml, ffmpeg_command=False):
    def list_to_string(list_input: list):
        return_str = ''
        for item in list_input:
            return_str += item + ","

        return return_str[:-1]

    execute = []

    for item in section:
        if section[item] is not None:

            # if the item is any value but 'true', append both the key and value
            if section[item] is not True:

                if type(section[item]) is list and ffmpeg_command is True:
                    execute.append(str(item))
                    execute.append(list_to_string(section[item]))

                else:
                    execute.append(str(item))
                    execute.append(str(section[item]))

            # if it's set to true, simply append the key
            else:
                execute.append(str(item))

    return execute