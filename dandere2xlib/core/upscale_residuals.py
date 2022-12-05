import logging
import threading
import time

from threading import Thread
from typing import List

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
        self.__logger = logging.getLogger(dandere2x_session.input_video_path.name)

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
                    # print(f"position of {pos}")
                    d2x_image = self.__manager.residual_images[pos]

                    d2x_upscaled = w2x_server.upscale_d2x_frame(d2x_image)

                    self.__manager.residual_images_upscaled[pos] = d2x_upscaled
                    success = True
                except:
                    self.__logger.warning(f"Warning, frame {pos} failed. Need to try again (this is normal, up to 3 "
                                          "times, then it is likely bugged.).")
                    pass

        w2x_server.kill_server()

    def run(self) -> None:

        list_of_threads: List[Thread] = []

        for x in range(self.dandere2x_session.num_waifu2x_threads):

            ports = self.dandere2x_session.output_options['waifu2x_ncnn_vulkan']['client_ports'][f'client{x}']

            t1 = threading.Thread(target=self.__waifu2x_thread,
                                  args=(ports['receive_port'],
                                        ports['send_port'],
                                        x,
                                        self.dandere2x_session.num_waifu2x_threads))
            list_of_threads.append(t1)

        for waifu2x_thread in list_of_threads:
            waifu2x_thread.start()
            time.sleep(0.5)

        for waifu2x_thread in list_of_threads:
            waifu2x_thread.join()
