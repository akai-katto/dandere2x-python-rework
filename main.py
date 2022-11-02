import copy
import math
import threading
import time
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image as im
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement
from dandere2xlib.ffmpeg.VideoFrameExtractor import VideoFrameExtractor


def copy_from(A: np.ndarray, B: np.ndarray,
              A_start: Tuple[int, int], B_start: Tuple[int, int], B_end: Tuple[int, int]):
    """
    A_start is the index with respect to A of the upper left corner of the overlap
    B_start is the index with respect to B of the upper left corner of the overlap
    B_end is the index of with respect to B of the lower right corner of the overlap
    """
    try:
        A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])
        shape = B_end - B_start
        B_slices = tuple(map(slice, B_start, B_end + 1))
        A_slices = tuple(map(slice, A_start, A_start + shape + 1))
        B[B_slices] = A[A_slices]

    except ValueError:
        D2xFrame.LOGGING.info("fatal error copying block")
        raise ValueError


frame = D2xFrame.from_file(
    "C:\\Users\\tylerpc\\Documents\\GitHub\\dandere2x\\src\\workspace\\gui\\subworkspace\\inputs\\frame1.png")
print(frame.width)
print(frame.height)

frame.compress_frame_for_computations(5)

manager = D2xManagement()

extractor = VideoFrameExtractor(ffmpeg_binary=Path("C:\\ffmpeg\\ffmpeg.exe"),
                                input_video=Path("C:\\Users\\tylerpc\\Desktop\\3.7\\workspace\\yn_moving.mkv"),
                                width=1920,
                                height=1080)
block_size = 30
frame_count = 50


def part1():
    for x in range(frame_count):
        frame = extractor.get_frame()
        manager.input_images_array[x] = frame


def part2():
    for x in range(frame_count):
        while manager.input_images_array[x] is None:
            time.sleep(0.001)

        frame = manager.input_images_array[x]
        compressed = copy.deepcopy(frame)
        compressed.compress_frame_for_computations(95)
        manager.compressed_frames_array[x] = compressed


def part3():
    while manager.input_images_array[0] is None:
        time.sleep(0.0001)

    for frame_pos in range(0, frame_count - 1):

        while manager.input_images_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        while manager.compressed_frames_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        f1 = manager.input_images_array[frame_pos]
        f2 = manager.input_images_array[frame_pos + 1]
        f2_compressed = manager.compressed_frames_array[frame_pos + 1]

        array_subtracted_squared: np.array = (f2.frame_array - f1.frame_array) ** 2
        compressed_subtracted_squared: np.array = (f2_compressed.frame_array - f2.frame_array) ** 2

        matched_mean = np.einsum(
            "ijklm->ik",
            array_subtracted_squared.reshape(
                int(1080 / block_size), block_size,
                int(1920 / block_size), block_size,
                -1
            ),
            dtype=np.float32,
        )

        compressed_mean = np.einsum(
            "ijklm->ik",
            compressed_subtracted_squared.reshape(
                int(1080 / block_size), block_size,
                int(1920 / block_size), block_size,
                -1
            ),
            dtype=np.float32,
        )

        missing_blocks = []
        compared = matched_mean - compressed_mean
        empty_frame = D2xFrame(1920, 1080)
        for y in range(int(1080 / block_size)):
            for x in range(int(1920 / block_size)):
                if compared[y][x] <= 0:
                    empty_frame.copy_block(f1, block_size, x * block_size, y * block_size, x * block_size,
                                           y * block_size)
                else:
                    missing_blocks.append((x * block_size, y * block_size))

        empty_frame.save(Path(f"./outputs1/here{frame_pos}.png"))

        manager.missing_blocks[frame_pos] = missing_blocks


def part4():
    for pos in range(frame_count - 1):
        while manager.missing_blocks[pos] is None:
            time.sleep(0.0001)
        while manager.input_images_array[pos] is None:
            time.sleep(0.0001)

        missing_blocks = manager.missing_blocks[pos]
        f1 = manager.input_images_array[pos]

        dim = math.ceil(math.sqrt(len(missing_blocks))) + 1
        residual_image = D2xFrame(dim * block_size, dim * block_size)

        x_dim = 0
        y_dim = 0
        for missing_block in missing_blocks:
            x, y = missing_block
            if x_dim >= dim:
                x_dim = 0
                y_dim += 1
            residual_image.copy_block(f1, block_size, x, y,
                                      y_dim * block_size, x_dim * block_size)

            x_dim += 1

        residual_image.save(f"./outputs2/here{pos}.png")


start_time = time.time()
# t1 = threading.Thread(target=part1)
# t1.start()
# t2 = threading.Thread(target=part2)
# t2.start()
# t3 = threading.Thread(target=part3)
# t3.start()
# t4 = threading.Thread(target=part4)
# t4.start()
#
# t1.join()
# t2.join()
# t3.join()
# t4.join()

part1()
part2()
part3()
part4()
# part4()


print(time.time() - start_time)
