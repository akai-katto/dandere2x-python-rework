from time import sleep

import yaml
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow

from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from gui.dandere2_gui_session_statistics import Dandere2xGuiSessionStatistics
from gui.dandere2x_session_statistics_window import Ui_SessionStatistics


class Dandere2xSessionStatisticsImplementation(QMainWindow):
    def __init__(self, dandere2x_main_window_implementation: 'Dandere2xMainWindowImplementation'):
        super(Dandere2xSessionStatisticsImplementation, self).__init__()
        self.ui = Ui_SessionStatistics()
        self.ui.setupUi(self)

        self.dandere2x_main_window_implementation = dandere2x_main_window_implementation

        self.update_thread = QtStatisticsUpdater(self)
        self.update_thread.start()


class QtStatisticsUpdater(QtCore.QThread):

    def __init__(self, parent: Dandere2xSessionStatisticsImplementation):
        super(QtStatisticsUpdater, self).__init__(parent)
        self.parent = parent

    def run(self):
        while True:
            self.parent.ui.label_session_statistics_current_frame.setText(str(self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.current_frame).rjust(7))
            self.parent.ui.label_session_statistics_frames_remaining.setText(str(self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.frame_count - self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.current_frame).rjust(7))

            num = self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.total_pixels_count  - self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.pixels_upscaled_count
            denom = self.parent.dandere2x_main_window_implementation.dandere2x_gui_session_statistics.total_pixels_count
            try:
                recycled_pixels_ratio = round((num / denom), 3)
            except ZeroDivisionError:
                recycled_pixels_ratio = "N/A"

            self.parent.ui.label_d2x_statistics_recycled_pixels_ratio.setText(str(recycled_pixels_ratio).rjust(7))

            sleep(0.01)

