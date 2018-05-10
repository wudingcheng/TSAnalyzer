#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
import os
from qtpy.QtGui import *
from qtpy.uic import loadUi

class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent=parent)
        ui = os.path.join(os.path.dirname(__file__), "../resources/ui/about.ui")
        img = os.path.join(os.path.dirname(__file__), "../resources/images/icon.png")
        loadUi(ui, self)
        pix = QPixmap(img)
        self.imgLabel.setPixmap(pix)
