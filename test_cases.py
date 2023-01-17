import threading
import time
from pathlib import Path

import yaml

from dandere2xlib.d2x_frame import D2xFrame
from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.waifu2x.w2x_server import W2xServer


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
                            processing_type="singleprocess",
                            output_options=output_options)


def test_waifu2x(sendport, recvport):
    dandere2x_session = get_session()

    w2x_server = W2xServer(dandere2x_session=dandere2x_session, receive_port=sendport, send_port=recvport, gpu_id=0)
    w2x_server.start()
    d2x_image = D2xFrame(1920, 1080)

    for _ in range(100):
        start = time.time()
        d2x_upscaled1 = w2x_server.upscale_d2x_frame(d2x_image)
        print(f"took {time.time() - start}")

    w2x_server.kill_server()


def multi_threaded_performance_test():
    t1 = threading.Thread(target=test_waifu2x, args=(3509, 3510,))
    t2 = threading.Thread(target=test_waifu2x, args=(3511, 3512,))
    t3 = threading.Thread(target=test_waifu2x, args=(3513, 3514,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


if __name__ == "__main__":
    test_waifu2x(3510,3511)
    multi_threaded_performance_test()
