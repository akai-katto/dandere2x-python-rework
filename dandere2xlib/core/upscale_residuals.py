import logging
import threading
import time

from threading import Thread
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.waifu2x.w2x_server import W2xServer


class UpscaleResiduals(Thread):

    def __init__(self, manager: D2xManagement, dandere2x_session: Dandere2xSession):
        super().__init__()

        self.dandere2x_session = dandere2x_session

        self._HEIGHT = self.dandere2x_session.video_properties.corrected_video_height
        self._WIDTH = self.dandere2x_session.video_properties.corrected_video_width
        self._BLOCK_SIZE = self.dandere2x_session.block_size
        self._FRAME_COUNT = self.dandere2x_session.video_properties.input_video_settings.frame_count

        self.__manager = manager
        self.__loger = logging.getLogger()

    def __waifu2x_thread(self, receive_port, send_port, start, iter_val):
        print("starting thread 1")

        w2x_server = W2xServer(self.dandere2x_session, receive_port, send_port, 0)
        w2x_server.start()

        for pos in range(start, self._FRAME_COUNT - 1, iter_val):

            while self.__manager.residual_images[pos] is None:
                time.sleep(0.001)

            success = False
            while not success:
                try:
                    print(f"position of {pos}")
                    d2x_image = self.__manager.residual_images[pos]

                    d2x_upscaled = w2x_server.upscale_d2x_frame(d2x_image)

                    self.__manager.residual_images_upscaled[pos] = d2x_upscaled
                    success = True
                except:
                    print("it failed need to try again")
                    pass

        w2x_server.kill_server()

    def run(self) -> None:

        t1 = threading.Thread(target=self.__waifu2x_thread, args=(3509, 3510, 0, 2))
        t2 = threading.Thread(target=self.__waifu2x_thread, args=(3511, 3512, 1, 2))
        # t3 = threading.Thread(target=waifu2x_thread, args=(3513, 3514, 2, 3))
        # t4 = threading.Thread(target=waifu2x_thread, args=(3515, 3516, 3, 4))

        t1.start()
        time.sleep(.5)
        t2.start()
        # time.sleep(1)
        # t3.start()
        # time.sleep(1)
        # t4.start()

        t1.join()
        t2.join()
        # t3.join()
        # t4.join()