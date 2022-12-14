from PyQt6.QtWidgets import QMainWindow
from gui.dandere2x_settings_window import Ui_Dandere2xSettingsWindow


class Dandere2xSettingsWindowImplementation(QMainWindow):
    def __init__(self, dandere2x_main_window_implementation: 'Dandere2xMainWindowImplementation'):
        super(Dandere2xSettingsWindowImplementation, self).__init__()
        self.ui = Ui_Dandere2xSettingsWindow()
        self.ui.setupUi(self)

        self.dandere2x_main_window_implementation = dandere2x_main_window_implementation
        self.wire_combo_boxes()

    def wire_combo_boxes(self):
        self.ui.combo_box_dandere2x_settings_scale_factor.currentIndexChanged.connect(self.dandere2x_main_window_implementation.refresh_output_texts)
