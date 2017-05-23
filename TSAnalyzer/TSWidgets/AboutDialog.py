# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TSAnalyzer/TSWidgets/about.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_aboutWidget(object):
    def setupUi(self, aboutWidget):
        aboutWidget.setObjectName("aboutWidget")
        aboutWidget.resize(496, 342)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(aboutWidget.sizePolicy().hasHeightForWidth())
        aboutWidget.setSizePolicy(sizePolicy)
        aboutWidget.setMinimumSize(QtCore.QSize(496, 342))
        aboutWidget.setMaximumSize(QtCore.QSize(496, 342))
        aboutWidget.setStyleSheet("font: 75 10pt \"Microsoft Yahei\";\n"
"background-color: rgb(255, 255, 255);")
        self.verticalLayout = QtWidgets.QVBoxLayout(aboutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imgLabel = QtWidgets.QLabel(aboutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgLabel.sizePolicy().hasHeightForWidth())
        self.imgLabel.setSizePolicy(sizePolicy)
        self.imgLabel.setMinimumSize(QtCore.QSize(80, 80))
        self.imgLabel.setMaximumSize(QtCore.QSize(80, 80))
        self.imgLabel.setText("")
        self.imgLabel.setPixmap(QtGui.QPixmap(":/新前缀/icon.png"))
        self.imgLabel.setScaledContents(True)
        self.imgLabel.setObjectName("imgLabel")
        self.horizontalLayout.addWidget(self.imgLabel)
        self.label_2 = QtWidgets.QLabel(aboutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(aboutWidget)
        self.label.setEnabled(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(aboutWidget)
        QtCore.QMetaObject.connectSlotsByName(aboutWidget)

    def retranslateUi(self, aboutWidget):
        _translate = QtCore.QCoreApplication.translate
        aboutWidget.setWindowTitle(_translate("aboutWidget", "PGTSAV"))
        self.label_2.setText(_translate("aboutWidget", "<html><head/><body><p align=\"center\">Python GNSS Time Series Analysis and Visualization</p><p align=\"center\">( TSAnalyzer )</p></body></html>"))
        self.label.setText(_translate("aboutWidget", "<html><head/><body><hr/><p>Author: WU Dingcheng, Ph.D. candinate</p><p>Email: wudingcheng14@mails.ucas.ac.cn</p><p>Insitute of Geodesy and Geophysics, Chinese Academy of Scienses</p><hr/><p>You can distribute the software or modify the codes for non-commerical use. </p><p>All rights copyright reserved. </p><p>License: GPL</p></body></html>"))

