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

        # Interesting metadata
        self.single_frame_upscale_time = 0

    def __waifu2x_thread(self, receive_port, send_port, gpuid,  start, iter_val):
        self.__logger.info(f"Starting waifu2x thread on {receive_port} and {send_port}.")

        w2x_server = W2xServer(self.dandere2x_session, receive_port, send_port, gpuid)
        w2x_server.start()

        failed_upscale = 0
        for pos in range(start, self._FRAME_COUNT - 1, iter_val):

            while self.__manager.residual_images[pos] is None:
                time.sleep(0.001)

            success = False
            upscale_time = time.time()
            while not success:
                try:
                    d2x_image = self.__manager.residual_images[pos]
                    d2x_upscaled = w2x_server.upscale_d2x_frame(d2x_image)

                    self.__manager.residual_images_upscaled[pos] = d2x_upscaled
                    success = True
                except:
                    self.__logger.warning(f"Warning, frame {pos} failed. Need to try again (this is normal, up to 3 "
                                          "times, then it is likely bugged.).")
                    failed_upscale += 1

            total_time = time.time() - upscale_time

            # record how long it took to upscale frame0, to use as metadata for front end
            if pos == 0:
                self.single_frame_upscale_time = total_time

        # Once we're done upscaling all the images, yank the server to death.
        w2x_server.kill_server()
        self.__logger.info(f"Total failed upscaled images: {failed_upscale} (this is fine as long as the number is "
                           f"small)")

    def run(self) -> None:

        list_of_threads: List[Thread] = []

        for x in range(self.dandere2x_session.num_waifu2x_threads):

            ports = self.dandere2x_session.output_options['waifu2x_ncnn_vulkan']['client_ports'][f'session{self.dandere2x_session.session_id}'][f'client{x}']

            t1 = threading.Thread(target=self.__waifu2x_thread,
                                  args=(ports['receive_port'],
                                        ports['send_port'],
                                        ports['gpuid'],
                                        x,
                                        self.dandere2x_session.num_waifu2x_threads))
            list_of_threads.append(t1)

        for waifu2x_thread in list_of_threads:
            waifu2x_thread.start()
            time.sleep(0.5)

        for waifu2x_thread in list_of_threads:
            waifu2x_thread.join()
