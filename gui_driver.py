import sys

from PyQt6.QtWidgets import QApplication

from gui.dandere2x_main_window_implementation import Dandere2xMainWindowImplementation

app = QApplication(sys.argv)

window = Dandere2xMainWindowImplementation()
window.show()

sys.exit(app.exec())