import os
import socket
import subprocess
import threading
import time
from pathlib import Path

from dandere2xlib.d2xframe import D2xFrame


class W2xServer(threading.Thread):
    """
    Starts a waifu2x server up
    """
    BINARY_LOCATION = Path("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-rework\\test_fork\\cmake-build-debug-visual-studio")

    def __init__(self, port):
        threading.Thread.__init__(self, name="W2xServer")

        self.port = port
        self.executable_location = W2xServer.BINARY_LOCATION / "waifu2x-ncnn-vulkan.exe"

    def run(self):
        pass
        # print(str(self.executable_location))
        # active_waifu2x_subprocess = subprocess.Popen(args=[str(self.executable_location), str(self.port)],
        #                                              cwd=str(self.BINARY_LOCATION))
        # active_waifu2x_subprocess.wait()

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)


    def upscale_d2x_frame(self, frame: D2xFrame) -> D2xFrame:
        def divide_chunks(input_list, n):
            for i in range(0, len(input_list), n):
                yield input_list[i:i + n]

        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, self.port))

        width = str(frame.width).ljust(6)
        height = str(frame.height).ljust(6)

        s.sendall(bytes(width, encoding='utf8'))
        print(s.recv(1))
        s.sendall(bytes(height, encoding='utf8'))
        print(s.recv(1))

        chunked = divide_chunks(frame.get_byte_array(), 1000000)

        for chunk in chunked:
            print("chunked")
            s.send(chunk)
            print(s.recv(1))

        print("sending done")
        s.send(b"done")
        s.close()


        host = 'localhost'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 3510))

        s.send(b"s")
        all_bytes = s.recv(500000000)

        d2x_frame = D2xFrame.from_bytes(all_bytes)

        print("recieved image")
        s.close()
        return d2x_frame

if __name__ == "__main__":
    print('hi')
    w2x_server = W2xServer(3509)
    w2x_server.start()

    d2x_image = D2xFrame.from_file("/temp/inputs\\frame0.png")

    d2x_upscaled1 = w2x_server.upscale_d2x_frame(d2x_image)
    # d2x_upscaled2 = w2x_server.upscale_d2x_frame(d2x_image)
    #
    d2x_upscaled1.save(Path("upscaled1.bmp"))
    # d2x_upscaled2.save(Path("upscaled2.png"))
    #
    # print("hi2")
