import datetime
import math
import os
import sys
from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog

from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.video_settings import VideoSettings
from gui.dandere2x_main_window import Ui_Dandere2xMainWindow
from gui.dandere2x_settings_window_implementation import Dandere2xSettingsWindowImplementation


class Dandere2xMainWindowImplementation(QMainWindow):


    def construct_dandere2x_session_from_gui(self):
        return Dandere2xSession(input_video_path=Path(self.input_file),
                                output_path=Path(self.output_file),
                                scale_factor=self.settings_ui.ui.combo_box_dandere2x_settings_scale_factor.currentText(),
                                noise_factor=self.settings_ui.ui.combo_box_waifu2x_settings_denoise_level.currentText(),
                                block_size=self.settings_ui.ui.combo_box_dandere2x_settings_block_size.currentText(),
                                quality=self.settings_ui.ui.combo_box_dandere2x_settings_quality_coeffecient,
                                num_waifu2x_threads=num_waifu2x_threads,
                                output_options=output_options)

    def __init__(self):
        super(Dandere2xMainWindowImplementation, self).__init__()
        self.ui = Ui_Dandere2xMainWindow()
        self.ui.setupUi(self)

        # Other UI's
        self.settings_ui: Dandere2xSettingsWindowImplementation = Dandere2xSettingsWindowImplementation(self)
        self.settings_ui.hide()

        # Class Specific
        self.this_folder = os.getcwd()
        self.input_file = ""
        self.output_file = ""
        self.video_settings: VideoSettings = None

        # Initial Setup
        self.setup_icons()
        self.wire_buttons()
        self.pre_select_video_state()

    # Setup
    def wire_buttons(self):
        self.ui.button_select_video.clicked.connect(self.button_press_select_file)
        self.ui.button_change_video.clicked.connect(self.button_press_select_file)
        self.ui.button_settings.clicked.connect(self.settings_ui.show)

    def pre_select_video_state(self):

        # Select Input
        self.ui.label_selected_file.hide()
        self.ui.label_selected_video_runtime.hide()
        self.ui.label_selected_video_frame_count.hide()
        self.ui.button_change_video.hide()

        # Select Output
        self.ui.label_output_name.hide()
        self.ui.label_output_resolution.hide()
        self.ui.button_change_output.hide()

    def setup_icons(self):
        self.ui.label_icon_load_video.setPixmap(QPixmap("gui/icons/load-action-floppy.png"))
        self.ui.label_icon_save_video.setPixmap(QPixmap("gui/icons/download-square-outline.png"))
        self.ui.label_icon_upscale.setPixmap(QPixmap("gui/icons/hd-display.png"))

    # Manipulations
    def post_select_video_state(self):

        # Select Video
        self.ui.label_selected_file.show()
        self.ui.label_selected_video_runtime.show()
        self.ui.label_selected_video_frame_count.show()
        self.ui.button_change_video.show()
        self.ui.button_select_video.hide()

        # Select Output
        self.ui.button_select_output.hide()
        self.ui.label_output_name.show()
        self.ui.label_output_resolution.show()
        self.ui.button_change_output.show()
        self.ui.button_upscale.setEnabled(True)

        self.refresh_output_texts()

    # Refreshes
    def refresh_output_texts(self):
        scale_factor = int(self.settings_ui.ui.combo_box_dandere2x_settings_scale_factor.currentText())

        resolution = f"{self.video_settings.width * scale_factor}x{self.video_settings.height * scale_factor}"
        self.ui.label_output_name.setText(self._metadata_text_generator("Output File:", self.output_file, 29))
        self.ui.label_output_resolution.setText(self._metadata_text_generator("Output Res:", resolution, 29))

    # Button Presses
    def button_press_select_file(self):

        self.input_file = self._load_file()

        if self.input_file == '':
            return

        path, name = os.path.split(self.input_file)

        # File
        self.ui.label_selected_file.setText(self._metadata_text_generator("File:", name, 21))
        # Duration
        self.video_settings = VideoSettings(Path(self.input_file))
        duration = str(datetime.timedelta(seconds=math.ceil(self.video_settings.seconds)))
        self.ui.label_selected_video_runtime.setText(self._metadata_text_generator("Duration:", duration, 21))
        # Frame Count
        self.ui.label_selected_video_frame_count.setText(self._metadata_text_generator("Frame Count:",
                                                                                       str(self.video_settings.frame_count),
                                                                                       21))
        self.output_file = "temp_output.mkv"
        self.post_select_video_state()


    # Utilities
    def _load_file(self) -> str:
        self.ui.w = QWidget()
        self.ui.w.resize(320, 240)

        filename = QFileDialog.getOpenFileName(self, 'Open File', self.this_folder)
        return filename[0]

    @staticmethod
    def _metadata_text_generator(keyword: str, data: str, line_width: int):
        """
        Formats strings like this:
        __metadata_text_generator("Video Name:", "some_video.mkv", 29)  --> "Video Name:        some_video.mkv"

        Used in displaying metadata upon video selection.
        """

        consumed_space = len(keyword) + len(data)
        unconsumed_space = line_width - consumed_space
        if unconsumed_space <= 0:
            DOT_DOT_DOT_LEN = 3

            redacted_count = line_width - (len(keyword) + len(data)) - DOT_DOT_DOT_LEN - 1
            data = "..." + data[-redacted_count:]

        whitespace = line_width - (len(keyword) + len(data))  # re-compute white space if it changed
        formatted_string = keyword + " " * whitespace + data
        return formatted_string
