import copy
import gc
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

from dandere2xlib.core.dandere2x_session import get_dandere2x_session
from dandere2xlib.d2xframe import D2xFrame
from dandere2xlib.d2xmanagement import D2xManagement, D2xResidualCoordinate
from dandere2xlib.ffmpeg.frames_to_video_pipe import FramesToVideoPipe
from dandere2xlib.ffmpeg.video_frame_extractor import VideoFrameExtractor
from dandere2xlib.utilities.dandere2x_utils import set_dandere2x_logger
from dandere2xlib.waifu2x import upscale_file
from dandere2xlib.waifu2x.w2x_server import W2xServer


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


WIDTH = 1280
HEIGHT = 720

total_active_processes = 0
block_size = 20
frame_count = 200

manager = D2xManagement()
dandere2x_session = get_dandere2x_session()

set_dandere2x_logger("")
def part1():
    extractor = VideoFrameExtractor(ffmpeg_binary=Path("C:\\ffmpeg\\ffmpeg.exe"),
                                    input_video=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\steal.mkv"),
                                    optional_args=[],
                                    width=WIDTH,
                                    height=HEIGHT)

    for pos in range(frame_count):

        while pos > manager.last_upscaled_frame + 120:
            time.sleep(0.001)
        print(f"on extracting frame {pos}")

        frame = extractor.get_frame()
        manager.input_images_array[pos] = frame
        # frame.save(Path(f"temp\\inputs\\frame{pos}.png"))


# add noise to images
def part1p2():
    optional_args = ["-vf", "noise=c1s=8:c0f=u"]

    extractor = VideoFrameExtractor(ffmpeg_binary=Path("C:\\ffmpeg\\ffmpeg.exe"),
                                    input_video=Path("C:\\Users\\windw0z\\Desktop\\sample_videos\\steal.mkv"),
                                    optional_args=optional_args,
                                    width=WIDTH,
                                    height=HEIGHT)

    for pos in range(frame_count):

        while pos > manager.last_upscaled_frame + 120:
            time.sleep(0.001)
        print(f"on extracting frame {pos}")

        frame = extractor.get_frame()
        manager.noised_images_array[pos] = frame


def part2():
    for x in range(frame_count):
        while manager.noised_images_array[x] is None:
            time.sleep(0.001)

        frame = manager.noised_images_array[x]
        compressed = copy.deepcopy(frame)
        compressed.compress_frame_for_computations(100)
        manager.compressed_frames_array[x] = compressed


def part3():
    while manager.input_images_array[0] is None:
        time.sleep(0.0001)

    f1 = D2xFrame(WIDTH, HEIGHT)
    for frame_pos in range(0, frame_count - 1):

        while manager.noised_images_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        while manager.compressed_frames_array[frame_pos + 1] is None:
            time.sleep(0.0001)

        f2 = copy.deepcopy(manager.noised_images_array[frame_pos + 1])
        f2_compressed = manager.compressed_frames_array[frame_pos + 1]

        array_subtracted_squared: np.array = \
            (f2.frame_array.astype(np.double) - f1.frame_array.astype(np.double)) ** 2
        compressed_subtracted_squared: np.array = \
            (f2_compressed.frame_array.astype(np.double) - f2.frame_array.astype(np.double)) ** 2

        matched_mean = np.einsum(
            "ijklm->ik",
            array_subtracted_squared.reshape(
                int(HEIGHT / block_size), block_size,
                int(WIDTH / block_size), block_size,
                -1
            ),
            dtype=np.double,
        )

        compressed_mean = np.einsum(
            "ijklm->ik",
            compressed_subtracted_squared.reshape(
                int(HEIGHT / block_size), block_size,
                int(WIDTH / block_size), block_size,
                -1
            ),
            dtype=np.double,
        )

        matched_blocks = []
        missing_blocks = []
        compared = (matched_mean * 10) - compressed_mean
        for y in range(int(HEIGHT / block_size)):
            for x in range(int(WIDTH / block_size)):
                if compared[y][x] <= 0:
                    matched_blocks.append((x * block_size, y * block_size))
                else:
                    missing_blocks.append((x * block_size, y * block_size))

        for matched_block in matched_blocks:
            x, y = matched_block
            f2.copy_block(f1, block_size,
                          x, y,
                          x, y)

        f1 = copy.deepcopy(f2)
        f1.save(Path(f"temp/pt2f1save/output{frame_pos}.png"))
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

        f1 = copy.deepcopy(manager.input_images_array[pos + 1])

        if len(missing_blocks) != 0:

            if len(missing_blocks) >= ((WIDTH / block_size) * (HEIGHT / block_size)) * .85:
                residual_image = f1
                manager.residual_images[pos] = residual_image
                manager.residual_blocks[pos] = []
                continue

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
            residual_image = D2xFrame(1, 1)
            manager.residual_blocks[pos] = []

        manager.residual_images[pos] = residual_image
        # residual_image.save(Path(f"temp\\residuals\\frame{pos}.png"))


# def run_iteration(position):
#     manager.active_w2x += 1
#     input_frame = manager.residual_images[position]
#
#     temp_residual = Path(f"temp/temp_residual{position}.png")
#     temp_residual_upscaled = Path(f"temp/temp_residual_upscaled{position}.png")
#
#     input_frame.save(temp_residual)
#     upscale_file(temp_residual, temp_residual_upscaled, 2)
#
#     loaded = False
#     while not loaded:
#         try:
#             loaded_image = D2xFrame.from_file(str(temp_residual_upscaled))
#             loaded = True
#         except:
#             pass
#     manager.residual_images_upscaled[position] = loaded_image
#
#     manager.active_w2x -= 1
#
# def part5():
#
#
#     for pos in range(frame_count - 1):
#
#         while manager.residual_images[pos] is None:
#             time.sleep(0.001)
#
#         while manager.active_w2x > 4:
#             time.sleep(0.001)
#
#         threading.Thread(target=run_iteration, args=[pos]).start()


def part5():
    def waifu2x_thread(receive_port, send_port, start, iter_val):
        print("starting thread 1")

        w2x_server1 = W2xServer(receive_port, send_port)
        w2x_server1.start()

        for pos in range(start, frame_count - 1, iter_val):

            while manager.residual_images[pos] is None:
                time.sleep(0.001)

            success = False
            while not success:
                try:
                    print(f"position of {pos}")
                    d2x_image = manager.residual_images[pos]

                    d2x_upscaled = w2x_server1.upscale_d2x_frame(d2x_image)
                    # d2x_upscaled.save(Path(f"temp/pt5_residuals_upscaled/frame{pos}.png"))
                    manager.residual_images_upscaled[pos] = d2x_upscaled
                    success = True
                except:
                    print("it failed need to try again")
                    pass

        w2x_server1.kill_server()

    t1 = threading.Thread(target=waifu2x_thread, args=(3509, 3510, 0, 2))
    t2 = threading.Thread(target=waifu2x_thread, args=(3511, 3512, 1, 2))
    # t3 = threading.Thread(target=waifu2x_thread, args=(3513, 3514, 2, 4))
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


def part6():
    BLEED = 1
    SCALE_FACTOR = 2

    frames_to_pipe = FramesToVideoPipe(Path("temp\\outputvideo.mkv"), dandere2x_session)
    frames_to_pipe.start()

    current_frame = D2xFrame(WIDTH * 2, HEIGHT * 2)
    for pos in range(frame_count - 1):
        while manager.residual_blocks[pos] is None:
            time.sleep(0.0001)
        while manager.residual_images_upscaled[pos] is None:
            time.sleep(0.0001)

        while manager.missing_blocks[pos] is None:
            time.sleep(0.0001)

        residual_undo = manager.residual_blocks[pos]
        missing_blocks = manager.missing_blocks[pos]
        residual_image: D2xFrame = copy.deepcopy(manager.residual_images_upscaled[pos])

        if len(missing_blocks) == 0 and len(residual_undo) == 0:
            pass
        elif len(missing_blocks) != 0 and len(residual_undo) == 0:
            current_frame = residual_image
        else:
            for residual in residual_undo:
                residual: D2xResidualCoordinate = residual
                current_frame.copy_block(frame_other=residual_image, block_size=block_size * SCALE_FACTOR,
                                  this_x=residual.x_start * 2,
                                  this_y=residual.y_start * 2,
                                  other_x=residual.residual_x * (block_size + BLEED * 2) * SCALE_FACTOR +
                                          (BLEED * SCALE_FACTOR),
                                  other_y=residual.residual_y * (block_size + BLEED * 2) * SCALE_FACTOR +
                                          (BLEED * SCALE_FACTOR))

        manager.last_upscaled_frame = pos

        # Collect Garbage
        manager.residual_images_upscaled[pos] = None
        manager.missing_blocks[pos] = None
        manager.compressed_frames_array[pos] = None
        manager.noised_images_array[pos] = None
        manager.input_images_array[pos] = None
        manager.residual_images[pos] = None
        manager.residual_blocks[pos] = None

        n = gc.collect()
        # print("Number of unreachable objects collected by GC:", n)
        frames_to_pipe.save(current_frame)

    frames_to_pipe.kill()


def part7():
    pass


start_time = time.time()
t1 = threading.Thread(target=part1)
t1.start()
t1p2 = threading.Thread(target=part1p2)
t1p2.start()

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
t1p2.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()

#
# part1()
# part2()
# part3()
# part4()
# part5()
# part6()

print(time.time() - start_time)
