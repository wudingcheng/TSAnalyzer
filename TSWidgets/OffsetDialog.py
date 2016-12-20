# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'offset.ui'
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
        Dialog.resize(241, 191)
        Dialog.setMaximumSize(QtCore.QSize(300, 280))
        Dialog.setStyleSheet(_fromUtf8(""))
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setMargin(3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setStyleSheet(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.offsetBox = QtGui.QComboBox(Dialog)
        self.offsetBox.setMaximumSize(QtCore.QSize(106, 16777215))
        self.offsetBox.setStyleSheet(_fromUtf8("font: 10"))
        self.offsetBox.setObjectName(_fromUtf8("offsetBox"))
        self.offsetBox.addItem(_fromUtf8(""))
        self.offsetBox.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.offsetBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setMaximumSize(QtCore.QSize(106, 16777215))
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.horizontalLayout_4.addWidget(self.dateEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.eqGroup = QtGui.QGroupBox(Dialog)
        self.eqGroup.setObjectName(_fromUtf8("eqGroup"))
        self.verticalLayout = QtGui.QVBoxLayout(self.eqGroup)
        self.verticalLayout.setContentsMargins(3, -1, 3, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.eqRadio = QtGui.QRadioButton(self.eqGroup)
        self.eqRadio.setChecked(True)
        self.eqRadio.setObjectName(_fromUtf8("eqRadio"))
        self.horizontalLayout_3.addWidget(self.eqRadio)
        self.expRadio = QtGui.QRadioButton(self.eqGroup)
        self.expRadio.setObjectName(_fromUtf8("expRadio"))
        self.horizontalLayout_3.addWidget(self.expRadio)
        self.logRadio = QtGui.QRadioButton(self.eqGroup)
        self.logRadio.setObjectName(_fromUtf8("logRadio"))
        self.horizontalLayout_3.addWidget(self.logRadio)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tauWidget = QtGui.QWidget(self.eqGroup)
        self.tauWidget.setObjectName(_fromUtf8("tauWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tauWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.taulLayout = QtGui.QHBoxLayout()
        self.taulLayout.setObjectName(_fromUtf8("taulLayout"))
        self.label_3 = QtGui.QLabel(self.tauWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.taulLayout.addWidget(self.label_3)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.taulLayout.addItem(spacerItem2)
        self.tauBox = QtGui.QSpinBox(self.tauWidget)
        self.tauBox.setMaximum(99999)
        self.tauBox.setProperty("value", 1)
        self.tauBox.setObjectName(_fromUtf8("tauBox"))
        self.taulLayout.addWidget(self.tauBox)
        self.gridLayout_2.addLayout(self.taulLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.tauWidget)
        self.verticalLayout_2.addWidget(self.eqGroup)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.cancelButton = QtGui.QPushButton(Dialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout_5.addWidget(self.cancelButton)
        self.confirmButton = QtGui.QPushButton(Dialog)
        self.confirmButton.setObjectName(_fromUtf8("confirmButton"))
        self.horizontalLayout_5.addWidget(self.confirmButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Offsets Editor", None))
        self.label.setText(_translate("Dialog", "Offset Type", None))
        self.offsetBox.setItemText(0, _translate("Dialog", "Equipment", None))
        self.offsetBox.setItemText(1, _translate("Dialog", "Earthquake", None))
        self.label_2.setText(_translate("Dialog", "Offset Date", None))
        self.dateEdit.setDisplayFormat(_translate("Dialog", "yyyy-MM-dd", None))
        self.eqGroup.setTitle(_translate("Dialog", "Earthquake Type", None))
        self.eqRadio.setText(_translate("Dialog", "Break", None))
        self.expRadio.setText(_translate("Dialog", "Exp", None))
        self.logRadio.setText(_translate("Dialog", "Log", None))
        self.label_3.setText(_translate("Dialog", "Decay Tau", None))
        self.cancelButton.setText(_translate("Dialog", "Delete", None))
        self.confirmButton.setText(_translate("Dialog", "Confirm", None))

