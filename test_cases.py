import threading
import time
from pathlib import Path

from dandere2xlib.d2x_frame import D2xFrame
from dandere2xlib.ffmpeg.ffmpeg_utils import migrate_tracks_contextless
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml
from dandere2xlib.waifu2x.w2x_server import W2xServer
from main import get_session


def test_waifu2x(sendport, recvport):

    dandere2x_session = get_session()

    w2x_server = W2xServer(dandere2x_session=dandere2x_session, receive_port=sendport, send_port=recvport, gpu_id=0)
    w2x_server.start()
    #w2x_server.kill_server()
    d2x_image = D2xFrame.from_file("workspace/output1.png")

    total_upscaled_images = 0
    for _ in range(100):
        start = time.time()
        d2x_upscaled1 = w2x_server.upscale_d2x_frame(d2x_image)
        #d2x_upscaled1.save(Path("here.png"))
        #d2x_upscaled2 = w2x_server.upscale_d2x_frame(D2xFrame.from_file("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\temp\\residuals\\frame2.png"))
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


def test_migration_tracks():

    test_waifu2x(3509, 3510)
    # session = get_dandere2x_session()
    #
    # migrate_tracks_contextless(ffmpeg_dir=Path(load_executable_paths_yaml()["ffmpeg"]),
    #                            no_audio_file=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\nosound.mp4"),
    #                            input_file=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\shortvideo.mp4"),
    #                            output_file=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\migrated.mp4"),
    #                            output_options=session.output_options,
    #                            console_output_dir=None)

if __name__ == "__main__":
    multi_threaded_performance_test()
    #test_migration_tracks()