# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TSAnalyzer/TSWidgets/sigseg.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(794, 636)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.setObjectName("vlayout")
        self.gridLayout_2.addLayout(self.vlayout, 0, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(3, 9, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        self.listWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deleteButton = QtWidgets.QPushButton(self.groupBox)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.addButton = QtWidgets.QPushButton(self.groupBox)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sigseg Detection"))
        self.groupBox.setTitle(_translate("Dialog", "Detection Results"))
        self.deleteButton.setText(_translate("Dialog", "Delete"))
        self.addButton.setText(_translate("Dialog", "Add"))

