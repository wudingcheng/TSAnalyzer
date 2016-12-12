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
        aboutWidget.resize(498, 510)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(aboutWidget.sizePolicy().hasHeightForWidth())
        aboutWidget.setSizePolicy(sizePolicy)
        aboutWidget.setMinimumSize(QtCore.QSize(498, 510))
        aboutWidget.setMaximumSize(QtCore.QSize(498, 510))
        aboutWidget.setStyleSheet(_fromUtf8("font: 75 10pt \"Microsoft Yahei\";\n"
"background-color: rgb(255, 255, 255);"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(aboutWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.imgLabel = QtGui.QLabel(aboutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgLabel.sizePolicy().hasHeightForWidth())
        self.imgLabel.setSizePolicy(sizePolicy)
        self.imgLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.imgLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.imgLabel.setText(_fromUtf8(""))
        self.imgLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/新前缀/icon.png")))
        self.imgLabel.setScaledContents(True)
        self.imgLabel.setObjectName(_fromUtf8("imgLabel"))
        self.horizontalLayout.addWidget(self.imgLabel)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(aboutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(aboutWidget)
        QtCore.QMetaObject.connectSlotsByName(aboutWidget)

    def retranslateUi(self, aboutWidget):
        aboutWidget.setWindowTitle(_translate("aboutWidget", "PGTSAV", None))
        self.label.setText(_translate("aboutWidget", "<html><head/><body><p align=\"center\"><span style=\" font-weight:400;\">P</span>ython <span style=\" font-weight:400;\">G</span>NSS<span style=\" font-weight:400;\"> T</span>ime <span style=\" font-weight:400;\">S</span>eries <span style=\" font-weight:400;\">A</span>nalysis and <span style=\" font-weight:400;\">V</span>isualization</p><p align=\"center\">( TSAnalyzer )</p><hr/><p>Author: WU Dingcheng, Ph.D. candinate</p><p>Email: wudingcheng14@mails.ucas.ac.cn</p><p>Insitute of Geodesy and Geophysics, Chinese Academy of Scienses</p><hr/><p>You can distribute the software or modify the codes for non-commerical use. All rights copyright reserved. </p><p>License: GPL</p></body></html>", None))

