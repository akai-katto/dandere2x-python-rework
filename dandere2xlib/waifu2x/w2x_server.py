import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Final

from dandere2xlib.d2xframe import D2xFrame


class W2xServer(threading.Thread):
    """
    Starts a waifu2x server up
    """
    BINARY_LOCATION = Path("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-rework\\test_fork\\cmake-build-debug-visual-studio")
    METADATA_MSG_SIZE: Final = 1000
    THIRTY_TWO_MB = 32000000

    def __init__(self, receive_port, send_port):
        threading.Thread.__init__(self, name="W2xServer")

        self.receive_port = receive_port
        self.send_port = send_port
        self.executable_location = W2xServer.BINARY_LOCATION / "waifu2x-ncnn-vulkan.exe"
        self.total_upscaled_images = 0


    def run(self):
        print(str(self.executable_location))
        active_waifu2x_subprocess = subprocess.Popen(args=[str(self.executable_location),
                                                           str(self.receive_port),
                                                           str(self.send_port)],
                                                     cwd=str(self.BINARY_LOCATION))
        active_waifu2x_subprocess.wait()

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)

    def kill_server(self):
        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self.receive_port))
        s.send(b"exit".ljust(W2xServer.METADATA_MSG_SIZE - 1))
        s.recv(1)

    def upscale_d2x_frame(self, frame: D2xFrame) -> D2xFrame:

        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self.receive_port))

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
        s.connect((host, self.send_port))
        s.send(b"{"
               b"\"noise\": 3 ,"
               b" \"scale\": 2 ,"
               b" \"tilesize\": 200,"
               b" \"prepadding\": 18,"
               b" \"gpuid\": 0,"
               b" \"tta\": 0,"
               b" \"param_path\": \"models/models-cunet/noise3_scale2.0x_model.param\","
               b" \"model_path\": \"models/models-cunet/noise3_scale2.0x_model.bin\""
               b"}".ljust(W2xServer.METADATA_MSG_SIZE - 1))

        s.send(b" ")
        length = int(s.recv(20))
        s.send(b" ")

        all_bytes = s.recv(length)
        d2x_frame = D2xFrame.from_bytes(all_bytes)

        s.close()
        self.total_upscaled_images += 1
        return d2x_frame

if __name__ == "__main__":

    w2x_server = W2xServer(3509, 3510)
    w2x_server.start()
    #w2x_server.kill_server()
    d2x_image = D2xFrame.from_file("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\temp\\residuals\\frame1.png")

    total_upscaled_images = 0
    d2x_upscaled1 = w2x_server.upscale_d2x_frame(d2x_image)
    #d2x_upscaled2 = w2x_server.upscale_d2x_frame(D2xFrame.from_file("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\temp\\residuals\\frame2.png"))

    print(w2x_server.total_upscaled_images)
    w2x_server.kill_server()