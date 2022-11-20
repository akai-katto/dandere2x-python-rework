import copy
import io
import logging
import tempfile
import threading
import time
from pathlib import Path
from typing import Tuple

import imageio.v2 as imageio
import numpy
import numpy as np
from PIL import Image


class D2xFrame:
    """
    A wrapper that wraps dandere2x related functions around the PIL / Numpy library, primarily implementing tools and
    fail-safe checks that are much needed for dandere2x development.
    """

    LOGGING = logging.getLogger()

    def __init__(self, width: int, height: int, frame_name=None):
        """
        Instantiates a blank frame with bounds (height, width).

        @param width: Height of the image
        @param height: Width of the image
        @param frame_name: An optional name parameter to help with debugging.
        """
        self.frame_array: np.array = np.zeros([height, width, 3], dtype=np.uint8)
        self.__image_width: int = width
        self.__image_height: int = height

        if frame_name:
            self.frame_name = frame_name
        else:
            self.frame_name = "no frame_name set"

        self.logger = logging.getLogger(name=frame_name)

    # class methods #

    @classmethod
    def from_file(cls, file_path: str) -> 'D2xFrame':
        """
        Returns a Frame instance loading from a text file on disk.
        @param file_path: Location of the file on disk
        """

        image = imageio.imread(file_path).astype(np.uint8)
        instantiated_class = cls(image.shape[0], image.shape[1])
        instantiated_class.frame_name = file_path
        instantiated_class.frame_array = copy.copy(image)
        return instantiated_class

    @classmethod
    def from_ndarray(cls, frame_array: numpy.ndarray) -> 'D2xFrame':

        height = frame_array.shape[0]
        width = frame_array.shape[1]

        instantiated_frame = D2xFrame(width, height)
        instantiated_frame.frame_array = copy.copy(frame_array)

        return instantiated_frame

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> 'D2xFrame':
        img_byte_arr = io.BytesIO()
        img_byte_arr.write(raw_bytes)
        img_byte_arr.seek(0)

        image = imageio.imread(img_byte_arr, pilmode="RGB").astype(np.uint8)
        instantiated_class = cls(image.shape[0], image.shape[1])
        instantiated_class.frame_name = "loaded from bytes"
        instantiated_class.frame_array = copy.copy(image)
        return instantiated_class

    # static methods #

    @staticmethod
    def copy_from(A: np.ndarray, B: np.ndarray,
                  A_start: Tuple[int, int], B_start: Tuple[int, int], B_end: Tuple[int, int]):
        """
        A_start is the index with respect to A of the upper left corner of the overlap
        B_start is the index with respect to B of the upper left corner of the overlap
        B_end is the index of with respect to B of the lower right corner of the overlap
        """
        A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])
        shape = B_end - B_start
        B_slices = tuple(map(slice, B_start, B_end + 1))
        A_slices = tuple(map(slice, A_start, A_start + shape + 1))
        B[B_slices] = A[A_slices]

    # methods #

    def save(self, location: Path):
        save_image = self.get_pil_image()
        save_image.save(location, format='BMP')

    def save_detatch(self, location: Path):
        threading.Thread(target=self.save, args=[location]).start()

    def get_byte_array(self):

        img_byte_arr = io.BytesIO()
        self.get_pil_image().save(img_byte_arr, format='BMP')
        return img_byte_arr.getvalue()

    def create_buffered_image(self, buffer: int):
        bleed_frame_array: np.array = np.zeros([self.__image_height + buffer * 2, self.__image_width + buffer * 2, 3],
                                               dtype=np.uint8)
        self.copy_from(self.frame_array,
                       bleed_frame_array,
                       (0, 0),
                       (buffer, buffer), (self.__image_height + buffer - 1, self.__image_width + buffer - 1))

        self.__image_width = self.__image_width + buffer * 2
        self.__image_height = self.__image_height + buffer * 2
        self.frame_array = bleed_frame_array

    def get_pil_image(self):
        return Image.fromarray(self.frame_array.astype(np.uint8))

    def copy_block(self,
                   frame_other: 'D2xFrame',
                   block_size: int,
                   other_x: int, other_y: int,
                   this_x: int, this_y: int) -> None:
        """
        Check that we can validly copy a block before calling the numpy copy_from method. This way, detailed
        errors are given, rather than numpy just throwing an un-informative error.
        """
        # Check if inputs are valid before calling numpy copy_from
        #self.check_if_block_operation_valid(frame_other, block_size, other_x, other_y, this_x, this_y)

        D2xFrame.copy_from(frame_other.frame_array, self.frame_array,
                           (other_y, other_x), (this_y, this_x),
                           (this_y + block_size - 1, this_x + block_size - 1))

    def check_if_block_operation_valid(self,
                                       frame_other: 'D2xFrame',
                                       block_size: int,
                                       other_x: int, other_y: int,
                                       this_x: int, this_y: int) -> None:
        """
        Provide detailed reasons why a copy_block will not work before it's called. This method should access
        every edge case that could prevent copy_block from successfully working.
        """

        if this_x + block_size - 1 > self.width or this_y + block_size - 1 > self.height:
            self.logger.error('Input Dimensions Invalid for Copy Block Function, printing variables. Send akai_katto '
                              'this!')

            # Print Out Degenerate Values
            self.logger.error('this_x + block_size - 1 > self.width')
            self.logger.error(str(this_x + block_size - 1) + '?>' + str(self.width))

            self.logger.error('this_y + block_size - 1 > self.height')
            self.logger.error(str(this_y + block_size - 1) + '?>' + str(self.height))

            raise ValueError('Invalid Dimensions for Dandere2x Image, See Log. ')

        if other_x + block_size - 1 > frame_other.width or other_y + block_size - 1 > frame_other.height:
            self.logger.error('Input Dimensions Invalid for Copy Block Function, printing variables. Send Tyler this!')

            # Print Out Degenerate Values
            self.logger.error('other_x + block_size - 1 > frame_other.width')
            self.logger.error(str(other_x + block_size - 1) + '?>' + str(frame_other.width))

            self.logger.error('other_y + block_size - 1 > frame_other.height')
            self.logger.error(str(other_y + block_size - 1) + '?>' + str(frame_other.height))

            raise ValueError('Invalid Dimensions for Dandere2x Image, See Log. ')

        if this_x < 0 or this_y < 0:
            self.logger.error('Negative Input for \"this\" image')
            self.logger.error('x' + str(this_x))
            self.logger.error('y' + str(this_y))

            raise ValueError('Input dimensions invalid for copy block')

        if other_x < 0 or other_y < 0:
            raise ValueError('Input dimensions invalid for copy block')

    def compress_frame_for_computations(self, compression: int):
        pil_image = self.get_pil_image()

        with tempfile.SpooledTemporaryFile(suffix=".jpg") as tf:
            pil_image.save(tf, quality=compression, format="JPEG")
            tf.seek(0)
            self.frame_array: np.array = imageio.imread(tf).astype(np.uint8)

    # Getters #
    @property
    def width(self) -> int:
        return self.__image_width

    @property
    def height(self) -> int:
        return self.__image_height


if __name__ == "__main__":

    d2x_image = D2xFrame.from_file("C:\\Users\\windw0z\\Documents\\GitHub\\dandere2x-python-rework\\inputs\\frame0.png")

    start = time.time()
    d2x_image.get_byte_array()
    print(time.time() - start)