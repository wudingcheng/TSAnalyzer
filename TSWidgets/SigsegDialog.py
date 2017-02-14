# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sigseg.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(794, 636)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.setObjectName(_fromUtf8("vlayout"))
        self.matplotlibwidget = MatplotlibWidget(Dialog)
        self.matplotlibwidget.setObjectName(_fromUtf8("matplotlibwidget"))
        self.vlayout.addWidget(self.matplotlibwidget)
        self.gridLayout_2.addLayout(self.vlayout, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(3, 9, 3, 3)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.listWidget = QtGui.QListWidget(self.groupBox)
        self.listWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deleteButton = QtGui.QPushButton(self.groupBox)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.addButton = QtGui.QPushButton(self.groupBox)
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.horizontalLayout.addWidget(self.addButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Sigseg Detection", None))
        self.groupBox.setTitle(_translate("Dialog", "Detection Results", None))
        self.deleteButton.setText(_translate("Dialog", "Delete", None))
        self.addButton.setText(_translate("Dialog", "Add", None))

from matplotlibwidget import MatplotlibWidget
