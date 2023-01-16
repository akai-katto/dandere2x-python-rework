import datetime
import math
import os
import sys
import time
from pathlib import Path

import yaml
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog

from dandere2x_services.dandere2x_service_resolver import Dandere2xServiceResolver
from dandere2xlib.d2x_session import Dandere2xSession
from dandere2xlib.d2x_suspend_management import Dandere2xSuspendManagement
from dandere2xlib.ffmpeg.video_settings import VideoSettings
from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from gui.dandere2_gui_session_statistics import Dandere2xGuiSessionStatistics
from gui.dandere2x_about_implementation import Dandere2xAboutImplementation
from gui.dandere2x_main_window import Ui_Dandere2xMainWindow
from gui.dandere2x_session_statistics_implementation import Dandere2xSessionStatisticsImplementation
from gui.dandere2x_settings_window_implementation import Dandere2xSettingsWindowImplementation


class QtDandere2xThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal()

    def __init__(self,
                 parent,
                 dandere2x_session: Dandere2xSession,
                 dandere2x_gui_session_statistics: Dandere2xGuiSessionStatistics,
                 dandere2x_suspend_management: Dandere2xSuspendManagement):
        super(QtDandere2xThread, self).__init__(parent)

        self.dandere2x_session = dandere2x_session
        self.dandere2x_service = Dandere2xServiceResolver(dandere2x_session,
                                                          dandere2x_gui_session_statistics,
                                                          dandere2x_suspend_management)

    def run(self):
        self.dandere2x_service.start()
        self.join()

    def join(self):
        self.dandere2x_service.join()
        self.finished_signal.emit()


class Dandere2xMainWindowImplementation(QMainWindow):

    def get_dandere2x_session_from_gui(self):

        with open("config_files/output_options.yaml") as f:
            output_options = yaml.safe_load(f)

        output_options["dandere2x"]["multiprocess_thread_count"] = int(
            self.settings_ui.ui.combo_box_dandere2x_settings_multiprocess_thread_count.currentText())
        output_options["waifu2x_ncnn_vulkan"][
            "model"] = self.settings_ui.ui.combo_box_waifu2x_settings_model.currentText()
        output_options["waifu2x_ncnn_vulkan"]["tile_size"] = int(
            self.settings_ui.ui.combo_box_waifu2x_settings_tile_size.currentText())
        return Dandere2xSession(session_id=0,
                                input_video_path=Path(self.input_file),
                                output_path=Path(self.output_file),
                                workspace=Path("./workspace/workingspace"),
                                scale_factor=int(
                                    self.settings_ui.ui.combo_box_dandere2x_settings_scale_factor.currentText()),
                                noise_factor=int(
                                    self.settings_ui.ui.combo_box_waifu2x_settings_denoise_level.currentText()),
                                block_size=int(
                                    self.settings_ui.ui.combo_box_dandere2x_settings_block_size.currentText()),
                                quality=int(
                                    self.settings_ui.ui.combo_box_dandere2x_settings_quality_coeffecient.currentText()),
                                num_waifu2x_threads=int(
                                    self.settings_ui.ui.combo_box_waifu2x_settings_waifu2x_processes.currentText()),
                                processing_type=self.settings_ui.ui.combo_box_dandere2x_settings_process_type.currentText(),
                                output_options=output_options)

    def __init__(self):
        super(Dandere2xMainWindowImplementation, self).__init__()
        self.ui = Ui_Dandere2xMainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('gui/icons/d2x_ico.png'))

        # Class Specific
        self.this_folder = os.getcwd()
        self.input_file: Path = Path("")
        self.output_file: Path = Path("")
        self.video_settings: VideoSettings = None
        self.dandere2x_gui_session_statistics = Dandere2xGuiSessionStatistics()
        self.dandere2x_suspend_management = Dandere2xSuspendManagement()
        self.dandere2x_gui_is_running = True

        # Other UI's
        self.settings_ui: Dandere2xSettingsWindowImplementation = Dandere2xSettingsWindowImplementation(self)
        self.settings_ui.hide()

        self.session_statistics_ui: Dandere2xSessionStatisticsImplementation =\
            Dandere2xSessionStatisticsImplementation(self)
        self.session_statistics_ui.hide()

        self.about_dandere2x_ui = Dandere2xAboutImplementation()
        self.about_dandere2x_ui.hide()

        # Subthreads
        self.upscale_frame_of_updater = QtUpscaleFrameOfUpdater(self)
        self.upscale_frame_of_updater.start()

        self.dandere2x_thread: QtDandere2xThread = None

        # Initial Setup
        self.setup_icons()
        self.wire_buttons()
        self.pre_select_video_state()
        self.pre_upscale_state()

    # Setup
    def wire_buttons(self):
        self.ui.button_select_video.clicked.connect(self.button_press_select_file)
        self.ui.button_change_video.clicked.connect(self.button_press_select_file)
        self.ui.button_settings.clicked.connect(self.settings_ui.show)
        self.ui.button_change_output.clicked.connect(self.press_change_output_button)
        self.ui.button_upscale.clicked.connect(self.press_upscale_button)
        self.ui.button_statistics.clicked.connect(self.session_statistics_ui.show)
        self.ui.button_about.clicked.connect(self.about_dandere2x_ui.show)
        self.ui.button_suspend.clicked.connect(self.suspend_toggle)

    def pre_select_video_state(self):

        # Select Input
        self.ui.label_selected_file_lhs.hide()
        self.ui.label_selected_file_rhs.hide()
        self.ui.label_selected_video_runtime_lhs.hide()
        self.ui.label_selected_video_runtime_rhs.hide()
        self.ui.label_selected_video_frame_count_lhs.hide()
        self.ui.label_selected_video_frame_count_rhs.hide()
        self.ui.button_change_video.hide()

        # Select Output
        self.ui.label_output_name_lhs.hide()
        self.ui.label_output_name_rhs.hide()
        self.ui.label_output_resolution_lhs.hide()
        self.ui.label_output_resolution_rhs.hide()
        self.ui.button_change_output.hide()

    def pre_upscale_state(self):
        self.ui.label_progress_bar.hide()
        self.ui.label_upscale_frame_of_lhs.hide()
        self.ui.label_upscale_frame_of_rhs.hide()
        self.ui.button_suspend.hide()

    def setup_icons(self):
        self.ui.label_icon_load_video.setPixmap(QPixmap("gui/icons/load-action-floppy.png"))
        self.ui.label_icon_save_video.setPixmap(QPixmap("gui/icons/download-square-outline.png"))
        self.ui.label_icon_upscale.setPixmap(QPixmap("gui/icons/2x.png"))
        self.ui.label_progress_bar.setPixmap(QPixmap("gui/icons/progressbar0.png"))

    # Manipulations
    def post_select_video_state(self):

        # Select Video
        self.ui.label_selected_file_lhs.show()
        self.ui.label_selected_file_rhs.show()
        self.ui.label_selected_video_runtime_lhs.show()
        self.ui.label_selected_video_runtime_rhs.show()
        self.ui.label_selected_video_frame_count_lhs.show()
        self.ui.label_selected_video_frame_count_rhs.show()
        self.ui.button_change_video.show()
        self.ui.button_select_video.hide()

        # Select Output
        self.ui.button_select_output.hide()
        self.ui.label_output_name_lhs.show()
        self.ui.label_output_name_rhs.show()
        self.ui.label_output_resolution_lhs.show()
        self.ui.label_output_resolution_rhs.show()
        self.ui.button_change_output.show()
        self.ui.button_upscale.setEnabled(True)

        self.refresh_output_texts()

    def upscale_in_progress_state(self):

        self.ui.label_progress_bar.show()
        self.ui.label_upscale_frame_of_lhs.show()
        self.ui.label_upscale_frame_of_rhs.show()
        self.ui.button_upscale.hide()
        self.ui.button_change_video.setEnabled(False)
        self.ui.button_change_output.setEnabled(False)
        self.ui.button_suspend.show()

    def post_upscale_state(self):
        self.ui.label_progress_bar.hide()
        self.ui.label_upscale_frame_of_lhs.hide()
        self.ui.label_upscale_frame_of_rhs.hide()
        self.ui.button_upscale.show()
        self.ui.button_change_video.setEnabled(True)
        self.ui.button_change_output.setEnabled(True)
        self.ui.button_suspend.hide()

    def suspend_toggle(self):
        if self.dandere2x_suspend_management.is_suspended():
            self.ui.button_suspend.setText("Suspend")
            self.dandere2x_suspend_management.unsuspend()
        else:
            self.ui.button_suspend.setText("Unsuspend")
            self.dandere2x_suspend_management.suspend()

    # Refreshes
    def refresh_output_texts(self):
        if self.input_file == Path(""):
            return

        scale_factor = int(self.settings_ui.ui.combo_box_dandere2x_settings_scale_factor.currentText())
        resolution = f"{self.video_settings.width * scale_factor}x{self.video_settings.height * scale_factor}"
        self.ui.label_output_name_rhs.setText(self.output_file.name)
        self.ui.label_output_resolution_rhs.setText(resolution)

    # Button Presses
    def button_press_select_file(self):

        self.input_file = Path(self._load_file())

        if self.input_file == Path(''):
            return

        path, name = os.path.split(self.input_file)

        # File
        self.ui.label_selected_file_rhs.setText(name)
        # Duration
        self.video_settings = VideoSettings(Path(self.input_file))
        duration = str(datetime.timedelta(seconds=math.ceil(self.video_settings.seconds)))
        self.ui.label_selected_video_runtime_rhs.setText(duration)
        # Frame Count
        self.ui.label_selected_video_frame_count_rhs.setText(str(self.video_settings.frame_count))
        self.output_file = Path(self.this_folder) / "workspace" / (self.input_file.stem + "_d2x" + self.input_file.suffix)
        self.post_select_video_state()

    def press_change_output_button(self):
        save_file_name = self._change_file_name()
        if save_file_name == '':  # don't change if nothing is selected
            return

        self.output_file = save_file_name

        name_only = Path(self.output_file).name
        self.ui.label_output_name_rhs.setText(name_only)

    def press_upscale_button(self):
        self.dandere2x_gui_session_statistics = Dandere2xGuiSessionStatistics()
        self.dandere2x_suspend_management = Dandere2xSuspendManagement()
        dandere2x_session = self.get_dandere2x_session_from_gui()

        self.dandere2x_thread = QtDandere2xThread(self,
                                                  dandere2x_session,
                                                  self.dandere2x_gui_session_statistics,
                                                  self.dandere2x_suspend_management)
        self.dandere2x_thread.start()
        self.dandere2x_thread.finished_signal.connect(self.post_upscale_state)
        self.upscale_in_progress_state()

    def closeEvent(self, event):
        self.dandere2x_gui_is_running = False
        time.sleep(0.1)  # need to sleep to avoid race conditions

    # Utilities
    def _load_file(self) -> str:
        filename = QFileDialog.getOpenFileName(self, 'Open File', self.this_folder)
        return filename[0]

    def _change_file_name(self):
        filter = f"*{Path(self.input_file).suffix}"

        default_name = self.output_file
        if self.output_file == '':
            default_name = self.this_folder

        filename = QFileDialog.getSaveFileName(self, 'Save File', str(default_name), filter)
        return filename[0]


class QtUpscaleFrameOfUpdater(QtCore.QThread):

    def __init__(self, parent: Dandere2xMainWindowImplementation):
        super(QtUpscaleFrameOfUpdater, self).__init__(parent)
        self.parent = parent

    @staticmethod
    def get_progress_bar(percentage: int):
        percent = round(percentage / 10)
        progress_bar = "⬛" * percent + "⬜" * (10 - percent)
        return progress_bar

    def run(self):
        while True and self.parent.dandere2x_gui_is_running:
            self.parent.ui.label_upscale_frame_of_rhs.setText(
                f"{self.parent.dandere2x_gui_session_statistics.current_frame}/{self.parent.dandere2x_gui_session_statistics.frame_count}")

            ratio = max(1, int((self.parent.dandere2x_gui_session_statistics.current_frame / self.parent.dandere2x_gui_session_statistics.frame_count) * 100))
            rounded_to_ten = round((min(100, ratio)) / 10)
            self.parent.ui.label_progress_bar.setPixmap(QPixmap(f"gui/icons/progressbar{rounded_to_ten}.png"))
            time.sleep(0.1)
