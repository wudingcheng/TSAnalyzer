# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
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

class Ui_aboutWidget(object):
    def setupUi(self, aboutWidget):
        aboutWidget.setObjectName(_fromUtf8("aboutWidget"))
        aboutWidget.resize(496, 342)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(aboutWidget.sizePolicy().hasHeightForWidth())
        aboutWidget.setSizePolicy(sizePolicy)
        aboutWidget.setMinimumSize(QtCore.QSize(496, 342))
        aboutWidget.setMaximumSize(QtCore.QSize(496, 342))
        aboutWidget.setStyleSheet(_fromUtf8("font: 75 10pt \"Microsoft Yahei\";\n"
"background-color: rgb(255, 255, 255);"))
        self.verticalLayout = QtGui.QVBoxLayout(aboutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.imgLabel = QtGui.QLabel(aboutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgLabel.sizePolicy().hasHeightForWidth())
        self.imgLabel.setSizePolicy(sizePolicy)
        self.imgLabel.setMinimumSize(QtCore.QSize(80, 80))
        self.imgLabel.setMaximumSize(QtCore.QSize(80, 80))
        self.imgLabel.setText(_fromUtf8(""))
        self.imgLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/新前缀/icon.png")))
        self.imgLabel.setScaledContents(True)
        self.imgLabel.setObjectName(_fromUtf8("imgLabel"))
        self.horizontalLayout.addWidget(self.imgLabel)
        self.label_2 = QtGui.QLabel(aboutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(aboutWidget)
        self.label.setEnabled(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(aboutWidget)
        QtCore.QMetaObject.connectSlotsByName(aboutWidget)

    def retranslateUi(self, aboutWidget):
        aboutWidget.setWindowTitle(_translate("aboutWidget", "PGTSAV", None))
        self.label_2.setText(_translate("aboutWidget", "<html><head/><body><p align=\"center\">Python GNSS Time Series Analysis and Visualization</p><p align=\"center\">( TSAnalyzer )</p></body></html>", None))
        self.label.setText(_translate("aboutWidget", "<html><head/><body><hr/><p>Author: WU Dingcheng, Ph.D. candinate</p><p>Email: wudingcheng14@mails.ucas.ac.cn</p><p>Insitute of Geodesy and Geophysics, Chinese Academy of Scienses</p><hr/><p>You can distribute the software or modify the codes for non-commerical use. </p><p>All rights copyright reserved. </p><p>License: GPL</p></body></html>", None))

