# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialog_window_file.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class UiDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(310, 329)
#         Dialog.setStyleSheet("background-image: url(:/images/img_f2dwsnZ2oAX5phbKn41y.png);\n"
# "")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(10, 10, 291, 311))
        self.frame.setStyleSheet("background-color: none;\n"
"border-radius: 10px;\n"
"border: 0px solid  rgba(255, 255, 255, 250);")
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: none;\n"
"font-size: 18pt;\n"
"border: none;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.frame)
        self.comboBox.setStyleSheet("QComboBox {\n"
"background-color: rgba(15, 15, 15, 150);\n"
"color: rgba(255, 255, 255, 255);\n"
"border: 1px solid rgba(255, 255, 255, 255);\n"
"border-radius: 7px;\n"
"font-size: 12pt;\n"
"}\n"
"\n"
"QComboBox::hover {\n"
"background-color: rgba(14, 77, 201, 255);\n"
"}\n"
"\n"
"QComboBox::item {\n"
"color: rgba(255, 255, 255, 255);\n"
"}")
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setStyleSheet("background-color: rgba(255, 255, 255, 30);\n"
"border-radius: 7px;\n"
"border: none;\n"
"border: 1px solid rgba(255, 255, 255, 255);")
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.comboBox_2 = QtWidgets.QComboBox(self.frame)
        self.comboBox_2.setStyleSheet("QComboBox {\n"
"background-color: rgba(15, 15, 15, 150);\n"
"color: rgba(255, 255, 255, 255);\n"
"border: 1px solid rgba(255, 255, 255, 255);\n"
"border-radius: 7px;\n"
"font-size: 12pt;\n"
"}\n"
"\n"
"QComboBox::hover {\n"
"background-color: rgba(14, 77, 201, 255);\n"
"}\n"
"\n"
"QComboBox::item {\n"
"color: rgba(255, 255, 255, 255);\n"
"}")
        self.comboBox_2.setObjectName("comboBox_2")
        self.verticalLayout.addWidget(self.comboBox_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton_set = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton_set.setFont(font)
        self.pushButton_set.setStyleSheet("QPushButton {\n"
"background-color: rgba(15, 15, 15, 150);\n"
"color: rgba(255, 255, 255, 255);\n"
"border: 1px solid rgba(255, 255, 255, 255);\n"
"border-radius: 7px;\n"
"font-size: 16pt;\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"background-color: rgba(6, 176, 37, 255);\n"
"}")
        self.pushButton_set.setObjectName("pushButton_set")
        self.verticalLayout.addWidget(self.pushButton_set)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Окно добавления"))
        self.pushButton_set.setText(_translate("Dialog", "Применить"))
