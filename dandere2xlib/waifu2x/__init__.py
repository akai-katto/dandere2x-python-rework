import subprocess
from pathlib import Path


def upscale_file(input: Path, output: Path, scale_factor: int):
    w2x_path = "C:\\Users\\windw0z\\Desktop\\3.7\\externals\\waifu2x-ncnn-vulkan\\waifu2x-ncnn-vulkan.exe"

    exec_command = [w2x_path, "-i", str(input.absolute()), "-s", str(scale_factor), "-o", str(output.absolute())]
    active_waifu2x_subprocess = subprocess.Popen(exec_command, shell=False)
    active_waifu2x_subprocess.wait()


if __name__ == "__main__":
    upscale_file(Path("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\outputs3\\here0.png"),
                 Path("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\upscaled\\here0.png"),
                 2)