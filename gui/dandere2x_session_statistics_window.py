# Form implementation generated from reading ui file 'dandere2x_session_statistics_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SessionStatistics(object):
    def setupUi(self, SessionStatistics):
        SessionStatistics.setObjectName("SessionStatistics")
        SessionStatistics.resize(293, 300)
        self.label = QtWidgets.QLabel(SessionStatistics)
        self.label.setGeometry(QtCore.QRect(10, 10, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(False)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(SessionStatistics)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 141, 16))
        font = QtGui.QFont()
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(SessionStatistics)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 151, 16))
        font = QtGui.QFont()
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_session_statistics_current_frame = QtWidgets.QLabel(SessionStatistics)
        self.label_session_statistics_current_frame.setGeometry(QtCore.QRect(224, 50, 61, 20))
        font = QtGui.QFont()
        self.label_session_statistics_current_frame.setFont(font)
        self.label_session_statistics_current_frame.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_session_statistics_current_frame.setObjectName("label_session_statistics_current_frame")
        self.label_session_statistics_frames_remaining = QtWidgets.QLabel(SessionStatistics)
        self.label_session_statistics_frames_remaining.setGeometry(QtCore.QRect(224, 70, 61, 20))
        font = QtGui.QFont()
        self.label_session_statistics_frames_remaining.setFont(font)
        self.label_session_statistics_frames_remaining.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_session_statistics_frames_remaining.setObjectName("label_session_statistics_frames_remaining")
        self.label_4 = QtWidgets.QLabel(SessionStatistics)
        self.label_4.setGeometry(QtCore.QRect(8, 130, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(False)
        font.setUnderline(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(SessionStatistics)
        self.label_5.setGeometry(QtCore.QRect(10, 165, 156, 21))
        font = QtGui.QFont()
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_d2x_statistics_recycled_pixels_ratio = QtWidgets.QLabel(SessionStatistics)
        self.label_d2x_statistics_recycled_pixels_ratio.setGeometry(QtCore.QRect(228, 165, 56, 20))
        font = QtGui.QFont()
        self.label_d2x_statistics_recycled_pixels_ratio.setFont(font)
        self.label_d2x_statistics_recycled_pixels_ratio.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_d2x_statistics_recycled_pixels_ratio.setObjectName("label_d2x_statistics_recycled_pixels_ratio")

        self.retranslateUi(SessionStatistics)
        QtCore.QMetaObject.connectSlotsByName(SessionStatistics)

    def retranslateUi(self, SessionStatistics):
        _translate = QtCore.QCoreApplication.translate
        SessionStatistics.setWindowTitle(_translate("SessionStatistics", "Statistics"))
        self.label.setText(_translate("SessionStatistics", "Session Statistics"))
        self.label_2.setText(_translate("SessionStatistics", "Current Frame"))
        self.label_3.setText(_translate("SessionStatistics", "Frames Remaining"))
        self.label_session_statistics_current_frame.setText(_translate("SessionStatistics", "   9999"))
        self.label_session_statistics_frames_remaining.setText(_translate("SessionStatistics", "   9999"))
        self.label_4.setText(_translate("SessionStatistics", "D2x Statistics"))
        self.label_5.setText(_translate("SessionStatistics", "Recycled Pixels Ratio"))
        self.label_d2x_statistics_recycled_pixels_ratio.setText(_translate("SessionStatistics", "100.00%"))
