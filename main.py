import time
from pathlib import Path

import yaml

from dandere2xlib.core import Dandere2x
from dandere2xlib.d2xsession import Dandere2xSession


def get_dandere2x_session() -> Dandere2xSession:
    """
    :return: A testing version of dandere2x session.
    """

    with open("./config_files/output_options.yaml") as f:
        output_options = yaml.safe_load(f)

    with open("./config_files/executable_paths.yaml") as f:
        executable_paths = yaml.safe_load(f)

    return Dandere2xSession(video_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\test.mkv"),
                            output_path=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\test_2x.mkv"),
                            scale_factor=2,
                            noise_factor=3,
                            block_size=60,
                            quality=100,
                            output_options=output_options,
                            executable_paths=executable_paths)


dandere2x_session = get_dandere2x_session()

start = time.time()
d2x = Dandere2x(dandere2x_session)
d2x.process()
print(f"end: {time.time() - start}")