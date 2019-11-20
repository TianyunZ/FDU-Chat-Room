# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientMainUI.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(991, 516)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 448, 140, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 466, 91, 20))
        self.label_2.setObjectName("label_2")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 10, 201, 441))
        self.groupBox.setObjectName("groupBox")
        self.listWidget_2 = QtWidgets.QListWidget(self.groupBox)
        self.listWidget_2.setGeometry(QtCore.QRect(10, 20, 181, 411))
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget_2.raise_()
        # self.listWidget_4 = QtWidgets.QListWidget(self.groupBox)
        # self.listWidget_4.setGeometry(QtCore.QRect(10, 20, 161, 411))
        # self.listWidget_4.setObjectName("listWidget_4")
        # self.listWidget_4.raise_()
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(210, 10, 781, 461))
        self.groupBox_2.setObjectName("groupBox_2")
        self.listWidget = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget.setGeometry(QtCore.QRect(10, 20, 611, 341))
        self.listWidget.setObjectName("listWidget")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox_2)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 370, 361, 81))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton.setGeometry(QtCore.QRect(400, 370, 65, 35))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setGeometry(QtCore.QRect(400, 410, 65, 35))
        self.pushButton_2.setObjectName("pushButton_2")
        self.listWidget_3 = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget_3.setGeometry(QtCore.QRect(630, 40, 141, 321))
        self.listWidget_3.setObjectName("listWidget_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(630, 20, 71, 16))
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 721, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(MainWindow.sendMessage)
        self.pushButton_2.clicked.connect(MainWindow.leaveRoom)
        self.listWidget_2.itemDoubleClicked['QListWidgetItem*'].connect(MainWindow.enterRoom)
        self.listWidget_3.itemDoubleClicked['QListWidgetItem*'].connect(MainWindow.clickUserList)
        # self.listWidget_4.itemDoubleClicked['QListWidgetItem*'].connect(MainWindow.leaveRoom)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Client"))
        self.label.setText(_translate("MainWindow", "Connect Status："))
        self.label_2.setText(_translate("MainWindow", "Failure"))
        self.groupBox.setTitle(_translate("MainWindow", "Channels"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Room"))
        self.pushButton.setText(_translate("MainWindow", "Send"))
        self.pushButton_2.setText(_translate("MainWindow", "Leave"))
        self.label_3.setText(_translate("MainWindow", "UserList:"))

