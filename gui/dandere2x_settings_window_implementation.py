import yaml
from PyQt6.QtWidgets import QMainWindow
from gui.dandere2x_settings_window import Ui_Dandere2xSettingsWindow


class Dandere2xSettingsWindowImplementation(QMainWindow):
    def __init__(self, dandere2x_main_window_implementation: 'Dandere2xMainWindowImplementation'):
        super(Dandere2xSettingsWindowImplementation, self).__init__()
        self.ui = Ui_Dandere2xSettingsWindow()
        self.ui.setupUi(self)
        try:
            self.load_settings()
        except KeyError:
            pass

        self.dandere2x_main_window_implementation = dandere2x_main_window_implementation
        self.wire_combo_boxes()
        self.wire_buttons()

    def wire_buttons(self):
        self.ui.button_save.clicked.connect(self.save_settings)

    def load_settings(self):
        with open("./config_files/gui_config.yaml", "r") as f:
            settings = yaml.safe_load(f)

        self.ui.combo_box_dandere2x_settings_quality_coeffecient.setCurrentText(settings['dandere2x_settings']['quality_coefficient'])
        self.ui.combo_box_dandere2x_settings_block_size.setCurrentText(settings['dandere2x_settings']['block_size'])
        self.ui.combo_box_dandere2x_settings_scale_factor.setCurrentText(settings['dandere2x_settings']['scale_factor'])
        self.ui.combo_box_dandere2x_settings_process_type.setCurrentText(settings['dandere2x_settings']['processtype'])
        self.ui.combo_box_dandere2x_settings_multiprocess_thread_count.setCurrentText(settings['dandere2x_settings']['multiprocess_thread_count'])

        self.ui.combo_box_waifu2x_settings_denoise_level.setCurrentText(settings['waifu2x_settings']['denoise_level'])
        self.ui.combo_box_waifu2x_settings_model.setCurrentText(settings['waifu2x_settings']['model'])
        self.ui.combo_box_waifu2x_settings_tile_size.setCurrentText(settings['waifu2x_settings']['tile_size'])
        self.ui.combo_box_waifu2x_settings_waifu2x_processes.setCurrentText(settings['waifu2x_settings']['waifu2x_processes'])

    def save_settings(self):

        settings = {}
        settings['dandere2x_settings'] = {}
        settings['waifu2x_settings'] = {}

        settings['dandere2x_settings']['quality_coefficient'] = self.ui.combo_box_dandere2x_settings_quality_coeffecient.currentText()
        settings['dandere2x_settings']['block_size'] = self.ui.combo_box_dandere2x_settings_block_size.currentText()
        settings['dandere2x_settings']['scale_factor'] = self.ui.combo_box_dandere2x_settings_scale_factor.currentText()
        settings['dandere2x_settings']['processtype'] = self.ui.combo_box_dandere2x_settings_process_type.currentText()
        settings['dandere2x_settings']['multiprocess_thread_count'] = self.ui.combo_box_dandere2x_settings_multiprocess_thread_count.currentText()

        settings['waifu2x_settings']['denoise_level'] = self.ui.combo_box_waifu2x_settings_denoise_level.currentText()
        settings['waifu2x_settings']['model'] = self.ui.combo_box_waifu2x_settings_model.currentText()
        settings['waifu2x_settings']['tile_size'] = self.ui.combo_box_waifu2x_settings_tile_size.currentText()
        settings['waifu2x_settings']['waifu2x_processes'] = self.ui.combo_box_waifu2x_settings_waifu2x_processes.currentText()

        with open("config_files/gui_config.yaml", "w+") as f:
            yaml.dump(settings, f)

    def wire_combo_boxes(self):
        self.ui.combo_box_dandere2x_settings_scale_factor.currentIndexChanged.connect(self.dandere2x_main_window_implementation.refresh_output_texts)
