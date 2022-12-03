import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Final

from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xsession import Dandere2xSession


class W2xServer(threading.Thread):
    """
    Starts a waifu2x server up
    """
    METADATA_MSG_SIZE: Final = 1000
    THIRTY_TWO_MB = 32000000

    def __init__(self, dandere2x_session: Dandere2xSession, receive_port, send_port, gpu_id):
        threading.Thread.__init__(self, name="W2xServer")

        self.dandere2x_session = dandere2x_session

        self._gpu_id = gpu_id
        self._receive_port = receive_port
        self._send_port = send_port
        self._waifu2x_location = Path(dandere2x_session.executable_paths["w2x_vulkan_server"])
        self._executable_location = self._waifu2x_location / "waifu2x-ncnn-vulkan.exe"

        self._model_name = self.dandere2x_session.output_options["waifu2x_ncnn_vulkan"]["model_name"]
        self._noise_factor = self.dandere2x_session.noise_factor
        self._tile_size = self.dandere2x_session.output_options["waifu2x_ncnn_vulkan"]["tile_size"]
        self._pre_padding = self.dandere2x_session.output_options["waifu2x_ncnn_vulkan"]["pre_padding"]

    def run(self):
        print(str(self._executable_location))
        active_waifu2x_subprocess = subprocess.Popen(args=[str(self._executable_location.absolute()),
                                                           str(self._receive_port),
                                                           str(self._send_port)],
                                                     cwd=str(self._waifu2x_location.absolute()))
        active_waifu2x_subprocess.wait()

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)

    def kill_server(self):
        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self._receive_port))
        s.send(b"exit".ljust(W2xServer.METADATA_MSG_SIZE - 1))
        s.recv(1)

    def upscale_d2x_frame(self, frame: D2xFrame) -> D2xFrame:
        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self._receive_port))

        raw_bytes = "{" \
                    f"\"noise\": {self.dandere2x_session.scale_factor} ," \
                    " \"scale\": 2 ," \
                    f" \"tilesize\": {self._tile_size}," \
                    f" \"prepadding\": {self._pre_padding}," \
                    F" \"gpuid\": {self._gpu_id}," \
                    " \"tta\": 0," \
                    f" \"param_path\": \"models/{self._model_name}/noise{self._noise_factor}_scale2.0x_model.param\"," \
                    f" \"model_path\": \"models/{self._model_name}/noise{self._noise_factor}_scale2.0x_model.bin\"" \
                    "}".ljust(W2xServer.METADATA_MSG_SIZE - 1)

        s.send(bytes(raw_bytes, "utf-8"))
        s.recv(1)

        width = str(frame.width).ljust(W2xServer.METADATA_MSG_SIZE - 1)
        height = str(frame.height).ljust(W2xServer.METADATA_MSG_SIZE - 1)

        s.sendall(bytes(width, encoding='utf8'))
        s.recv(1)
        s.sendall(bytes(height, encoding='utf8'))
        s.recv(1)

        s.send(frame.get_byte_array().ljust(W2xServer.THIRTY_TWO_MB))
        s.close()

        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self._send_port))

        s.send(b" ")
        length = int(s.recv(20))
        s.send(b" ")

        all_bytes = s.recv(length)
        d2x_frame = D2xFrame.from_bytes(all_bytes)

        s.close()
        return d2x_frame


if __name__ == "__main__":
    pass
