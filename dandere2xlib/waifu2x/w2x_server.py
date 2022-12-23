import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Final

from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


class W2xServer(threading.Thread):
    """
    Starts a waifu2x server up
    """
    METADATA_MSG_SIZE: Final = 1000
    THIRTY_TWO_MB = 32000000

    @staticmethod
    def divide_chunks(input_list, n):
        for i in range(0, len(input_list), n):
            yield input_list[i:i + n]

    def __init__(self, dandere2x_session: Dandere2xSession, receive_port, send_port, gpu_id):
        threading.Thread.__init__(self, name="W2xServer")

        self.dandere2x_session = dandere2x_session

        self._gpu_id = gpu_id
        self._receive_port = receive_port
        self._send_port = send_port
        self._waifu2x_location = Path(load_executable_paths_yaml()["w2x_vulkan_server"])
        self._executable_location = self._waifu2x_location / "waifu2x-ncnn-vulkan.exe"

        self._model_name = self.dandere2x_session.output_options["waifu2x_ncnn_vulkan"]["model_name"]
        self._noise_factor = self.dandere2x_session.noise_factor
        self._tile_size = self.dandere2x_session.output_options["waifu2x_ncnn_vulkan"]["tile_size"]
        self._alive = True

    def run(self):
        print(str(self._executable_location))

        active_waifu2x_subprocess = subprocess.Popen(args=[str(self._executable_location.absolute()),
                                                           str(self._receive_port),
                                                           str(self._send_port)],
                                                     cwd=str(self._waifu2x_location.absolute()))
        active_waifu2x_subprocess.wait()

        poll = active_waifu2x_subprocess.poll()
        if poll != 0:
            print(f"Exit Code: {poll}")
            print("WARNING WAIFU2x CRASHED UNEXPECTEDLY")
            print(f"ports: {self._send_port} {self._receive_port}")

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)

    def kill_server(self):
        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self._receive_port))
        s.send(b"exit".ljust(W2xServer.METADATA_MSG_SIZE - 1))
        s.recv(1)

    def get_prepadding(self):
        scale_factor = min(self.dandere2x_session.scale_factor, 2)

        if self._model_name == "models-cunet" and scale_factor == 2:
            return 18
        if self._model_name == "models-cunet" and scale_factor == 1:
            return 28
        else:
            return 7

    def get_scale_representation(self):
        scale_factor = min(self.dandere2x_session.scale_factor, 2)
        if scale_factor == 2:
            return "_scale2.0x"
        if scale_factor == 1:
            return ""

    def upscale_d2x_frame(self, frame: D2xFrame) -> D2xFrame:
        host = 'localhost'

        connected = False
        while not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, self._receive_port))
                connected = True
            except:
                pass

        raw_bytes = "{" \
                    f"\"noise\": {self.dandere2x_session.noise_factor} ," \
                    f" \"scale\": {self.dandere2x_session.scale_factor} ," \
                    f" \"tilesize\": {self._tile_size}," \
                    f" \"prepadding\": {self.get_prepadding()}," \
                    f" \"gpuid\": {self._gpu_id}," \
                    " \"tta\": 0," \
                    f" \"param_path\": \"models/{self._model_name}/noise{self._noise_factor}{self.get_scale_representation()}_model.param\"," \
                    f" \"model_path\": \"models/{self._model_name}/noise{self._noise_factor}{self.get_scale_representation()}_model.bin\"" \
                    "}".ljust(W2xServer.METADATA_MSG_SIZE - 1)

        s.send(bytes(raw_bytes, "utf-8"))
        s.recv(1)

        width = str(frame.width).ljust(W2xServer.METADATA_MSG_SIZE - 1)
        height = str(frame.height).ljust(W2xServer.METADATA_MSG_SIZE - 1)

        s.sendall(bytes(width, encoding='utf8'))
        s.recv(1)
        s.sendall(bytes(height, encoding='utf8'))
        s.recv(1)

        chunks = self.divide_chunks(frame.get_byte_array(), 8192)
        for chunk in chunks:
            s.recv(1)
            s.send(chunk)
        s.recv(1)
        s.send(b"done")

        s.close()

        connected = False
        while not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, self._send_port))
                connected = True
            except:
                pass

        counter = 0
        all_bytes = bytearray()
        recv = b""
        while recv != b"done":
            counter += 1
            recv = s.recv(8192)
            s.send(b"a")
            if recv != b"done":
                all_bytes.extend(recv)
        s.close()
        print(f"counter: {counter}")

        d2x_frame = D2xFrame.from_bytes(all_bytes)
        return d2x_frame


if __name__ == "__main__":
    pass
