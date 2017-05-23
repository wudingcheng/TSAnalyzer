# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TSAnalyzer/TSWidgets/log.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(307, 497)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.logLabel = QtWidgets.QLabel(Dialog)
        self.logLabel.setObjectName("logLabel")
        self.verticalLayout.addWidget(self.logLabel)
        self.logEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.logEdit.setObjectName("logEdit")
        self.verticalLayout.addWidget(self.logEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.saveButton = QtWidgets.QPushButton(Dialog)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.logLabel.setText(_translate("Dialog", "Site Logs:"))
        self.saveButton.setText(_translate("Dialog", "Save Log"))
        self.cancelButton.setText(_translate("Dialog", "Close"))

