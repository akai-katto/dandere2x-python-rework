import copy
import math
import os.path
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image as im
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement, D2xResidualCoordinate
from dandere2xlib.ffmpeg.VideoFrameExtractor import VideoFrameExtractor
from dandere2xlib.waifu2x import upscale_file


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

total_active_processes = 0
manager = D2xManagement()

extractor = VideoFrameExtractor(ffmpeg_binary=Path("C:\\ffmpeg\\ffmpeg.exe"),
                                input_video=Path("C:\\Users\\windw0z\\Desktop\\3.7\\workspace\\clipped.mkv"),
                                width=1920,
                                height=1080)
block_size = 30
frame_count = 100


def part1():
    for x in range(frame_count):
        frame = extractor.get_frame()
        manager.input_images_array[x] = frame
        # frame.save(Path(f"inputs\\frame{x}.png"))


def part2():
    for x in range(frame_count):
        while manager.input_images_array[x] is None:
            time.sleep(0.001)

        frame = manager.input_images_array[x]
        compressed = copy.deepcopy(frame)
        compressed.compress_frame_for_computations(100)
        manager.compressed_frames_array[x] = compressed


def part3():
    while manager.input_images_array[0] is None:
        time.sleep(0.0001)

    f1 = D2xFrame(1920, 1080)
    for frame_pos in range(0, frame_count - 1):

        while manager.input_images_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        while manager.compressed_frames_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        f2 = copy.deepcopy(manager.input_images_array[frame_pos + 1])
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

        matched_blocks = []
        missing_blocks = []
        compared = matched_mean - compressed_mean
        for y in range(int(1080 / block_size)):
            for x in range(int(1920 / block_size)):
                if compared[y][x] <= 0:
                    matched_blocks.append((x * block_size, y * block_size))
                else:
                    missing_blocks.append((x * block_size, y * block_size))

        # if len(missing_blocks) > (1920 / 30) * (1080 / 30) * .95:
        #     missing_blocks = []

        for matched_block in matched_blocks:
            x, y = matched_block
            f2.copy_block(f1, block_size,
                          x, y,
                          x, y)

        print(len(missing_blocks))
        f1 = copy.deepcopy(f2)
        # f1.save(Path(f"pt2f1save/output{frame_pos}.png"))
        manager.missing_blocks[frame_pos] = missing_blocks


def part4():
    BUFFER = 5
    BLEED = 1

    for pos in range(frame_count - 1):
        while manager.missing_blocks[pos] is None:
            time.sleep(0.0001)
        while manager.input_images_array[pos] is None:
            time.sleep(0.0001)

        missing_blocks = manager.missing_blocks[pos]
        f1 = copy.deepcopy(manager.input_images_array[pos+1])

        if len(missing_blocks) != 0:
            f1.create_buffered_image(BUFFER)
            dim = math.ceil(math.sqrt(len(missing_blocks))) + 1
            residual_image = D2xFrame(dim * (block_size + BLEED * 2), dim * (block_size + BLEED * 2))

            residual_undo = []
            x_dim = 0
            y_dim = 0
            for missing_block in missing_blocks:
                x, y = missing_block
                if x_dim >= dim:
                    x_dim = 0
                    y_dim += 1
                residual_image.copy_block(f1, (block_size + BLEED * 2),
                                          x + BUFFER - BLEED, y + BUFFER - BLEED,
                                          x_dim * (block_size + BLEED * 2), y_dim * (block_size + BLEED * 2))

                residual_undo.append(D2xResidualCoordinate(x_start=x, y_start=y, residual_x=x_dim, residual_y=y_dim))
                x_dim += 1

            manager.residual_blocks[pos] = residual_undo
        else:
            residual_image = D2xFrame(1,1)
            manager.residual_blocks[pos] = []

        manager.residual_images[pos] = residual_image
        # residual_image.save(Path(f"residuals\\frame{pos}.png"))


def run_iteration(position):

    manager.active_w2x += 1
    input_frame = manager.residual_images[position]

    temp_residual = Path(f"temp/temp_residual{position}.png")
    temp_residual_upscaled = Path(f"temp/temp_residual_upscaled{position}.png")

    input_frame.save(temp_residual)
    upscale_file(temp_residual, temp_residual_upscaled, 2)

    loaded = False
    while not loaded:
        try:
            loaded_image = D2xFrame.from_file(str(temp_residual_upscaled))
            loaded = True
        except:
            pass
    manager.residual_images_upscaled[position] = loaded_image

    manager.active_w2x -= 1


def part5():


    for pos in range(frame_count - 1):

        while manager.residual_images[pos] is None:
            time.sleep(0.001)

        while manager.active_w2x > 4:
            time.sleep(0.001)

        threading.Thread(target=run_iteration, args=[pos]).start()

def part6():
    BLEED = 1
    SCALE_FACTOR = 2

    undone = D2xFrame(3840, 2160)
    for pos in range(frame_count - 1):
        while manager.residual_blocks[pos] is None:
            time.sleep(0.0001)
        while manager.residual_images_upscaled[pos] is None:
            time.sleep(0.0001)

        while manager.missing_blocks[pos] is None:
            time.sleep(0.0001)

        residual_undo = manager.residual_blocks[pos]
        missing_blocks = manager.missing_blocks[pos]
        residual_image: D2xFrame = manager.residual_images_upscaled[pos]

        if len(missing_blocks) == 0:
            pass
        else:
            for residual in residual_undo:
                residual: D2xResidualCoordinate = residual
                undone.copy_block(frame_other=residual_image, block_size=block_size * SCALE_FACTOR,
                                  this_x=residual.x_start * 2,
                                  this_y=residual.y_start * 2,
                                  other_x=residual.residual_x * (block_size + BLEED * 2) * SCALE_FACTOR + (
                                              BLEED * SCALE_FACTOR),
                                  other_y=residual.residual_y * (block_size + BLEED * 2) * SCALE_FACTOR + (
                                              BLEED * SCALE_FACTOR))
        undone.save(f"pt5\\frame{pos}.png")


start_time = time.time()
t1 = threading.Thread(target=part1)
t1.start()
t2 = threading.Thread(target=part2)
t2.start()
t3 = threading.Thread(target=part3)
t3.start()
t4 = threading.Thread(target=part4)
t4.start()
t5 = threading.Thread(target=part5)
t5.start()
t6 = threading.Thread(target=part6)
t6.start()
#
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()

# part1()
# part2()
# part3()
# part4()
# part5()
# part6()

print(time.time() - start_time)
