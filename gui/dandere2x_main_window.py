# Form implementation generated from reading ui file 'dandere2x_main_window.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dandere2xMainWindow(object):
    def setupUi(self, Dandere2xMainWindow):
        Dandere2xMainWindow.setObjectName("Dandere2xMainWindow")
        Dandere2xMainWindow.resize(731, 336)
        self.centralwidget = QtWidgets.QWidget(Dandere2xMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 90, 121, 111))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/icons/load-action-floppy.png"))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(300, 90, 121, 111))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/icons/download-square-outline.png"))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(530, 90, 131, 111))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/icons/hd-display.png"))
        self.label_3.setObjectName("label_3")
        self.button_select_video = QtWidgets.QPushButton(self.centralwidget)
        self.button_select_video.setGeometry(QtCore.QRect(70, 240, 111, 41))
        self.button_select_video.setObjectName("button_select_video")
        self.button_select_output = QtWidgets.QPushButton(self.centralwidget)
        self.button_select_output.setGeometry(QtCore.QRect(310, 240, 111, 41))
        self.button_select_output.setObjectName("button_select_output")
        self.button_upscale = QtWidgets.QPushButton(self.centralwidget)
        self.button_upscale.setGeometry(QtCore.QRect(540, 240, 111, 41))
        self.button_upscale.setObjectName("button_upscale")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(590, 7, 31, 41))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/icons/settings.png"))
        self.label_4.setObjectName("label_4")
        self.button_settings = QtWidgets.QPushButton(self.centralwidget)
        self.button_settings.setGeometry(QtCore.QRect(630, 15, 91, 24))
        self.button_settings.setObjectName("button_settings")
        self.button_change_video = QtWidgets.QPushButton(self.centralwidget)
        self.button_change_video.setGeometry(QtCore.QRect(80, 210, 91, 24))
        self.button_change_video.setObjectName("button_change_video")
        self.label_selected_file = QtWidgets.QLabel(self.centralwidget)
        self.label_selected_file.setGeometry(QtCore.QRect(50, 240, 151, 16))
        self.label_selected_file.setObjectName("label_selected_file")
        self.label_selected_video_runtime = QtWidgets.QLabel(self.centralwidget)
        self.label_selected_video_runtime.setGeometry(QtCore.QRect(50, 260, 151, 16))
        self.label_selected_video_runtime.setObjectName("label_selected_video_runtime")
        self.label_selected_video_frame_count = QtWidgets.QLabel(self.centralwidget)
        self.label_selected_video_frame_count.setGeometry(QtCore.QRect(50, 280, 151, 16))
        self.label_selected_video_frame_count.setObjectName("label_selected_video_frame_count")
        self.label_selected_video_runtime.raise_()
        self.label_selected_file.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.button_select_video.raise_()
        self.button_select_output.raise_()
        self.button_upscale.raise_()
        self.label_4.raise_()
        self.button_settings.raise_()
        self.button_change_video.raise_()
        self.label_selected_video_frame_count.raise_()
        Dandere2xMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Dandere2xMainWindow)
        self.statusbar.setObjectName("statusbar")
        Dandere2xMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(Dandere2xMainWindow)
        QtCore.QMetaObject.connectSlotsByName(Dandere2xMainWindow)

    def retranslateUi(self, Dandere2xMainWindow):
        _translate = QtCore.QCoreApplication.translate
        Dandere2xMainWindow.setWindowTitle(_translate("Dandere2xMainWindow", "Dandere2x"))
        self.button_select_video.setText(_translate("Dandere2xMainWindow", "Select Video"))
        self.button_select_output.setText(_translate("Dandere2xMainWindow", "Select Output"))
        self.button_upscale.setText(_translate("Dandere2xMainWindow", "Upscale!"))
        self.button_settings.setText(_translate("Dandere2xMainWindow", "Settings"))
        self.button_change_video.setText(_translate("Dandere2xMainWindow", "change video"))
        self.label_selected_file.setText(_translate("Dandere2xMainWindow", "File:             yn_moving.mkv"))
        self.label_selected_video_runtime.setText(_translate("Dandere2xMainWindow", "Duration:                   00:00:00"))
        self.label_selected_video_frame_count.setText(_translate("Dandere2xMainWindow", "Frame Count:                 7545"))
