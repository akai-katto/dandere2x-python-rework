from time import sleep

import yaml
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow

from dandere2xlib.utilities.dandere2x_utils import get_wait_delay
from gui.dandere2_gui_session_statistics import Dandere2xGuiSessionStatistics
from gui.dandere2x_about import Ui_AboutDandere2x
from gui.dandere2x_session_statistics_window import Ui_SessionStatistics


class Dandere2xAboutImplementation(QMainWindow):
    def __init__(self):
        super(Dandere2xAboutImplementation, self).__init__()
        self.ui = Ui_AboutDandere2x()
        self.ui.setupUi(self)
