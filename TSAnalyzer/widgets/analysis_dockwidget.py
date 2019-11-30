#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from ..utils import makeAction
from ..models.offsets import DISCONTINUITIES, DiscontinuityEvent
import os
from qtpy.QtGui import *
from qtpy.compat import getopenfilenames
from .timeseries_widget import TimeSeriesAnalysisWidget

def _(text, disambiguation=None, context='DiscontinuityDockWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class AnalysisDockWidget(QDockWidget):
    sig_outliers_clicked = Signal(dict)
    sig_fit_clicked = Signal(dict)
    sig_fit_batch = Signal(str, dict)
    sig_l1_clicked = Signal(dict)
    sig_l1_batch = Signal(str, dict)
    sig_data_changed = Signal(str)
    sig_data_saved = Signal()

    def __init__(self, parent=None):
        super(AnalysisDockWidget, self).__init__(parent=parent)
        self.tsAnalysisWidget = TimeSeriesAnalysisWidget(self)
        # self.tsAnalysisWidget.sig_outliers_clicked.connect(self.callback)
        self.tsAnalysisWidget.sig_outliers_clicked.connect(self.sig_outliers_clicked.emit)
        self.tsAnalysisWidget.sig_fit_clicked.connect(self.sig_fit_clicked.emit)
        self.tsAnalysisWidget.sig_l1_clicked.connect(self.sig_l1_clicked.emit)
        self.tsAnalysisWidget.sig_data_saved.connect(self.sig_data_saved)
        self.tsAnalysisWidget.sig_fit_batch.connect(lambda params: self.sig_fit_batch.emit("fit", params))
        self.tsAnalysisWidget.sig_l1_bacth.connect(lambda params: self.sig_l1_batch.emit("l1", params))
        self.tsAnalysisWidget.dataCombo.currentTextChanged.connect(self.sig_data_changed)
        self.__setupUI()
        self.stack.setEnabled(False)

    def __setupUI(self):
        self.setWindowTitle(_("Analysis"))
        self.stack = QStackedWidget()
        self.stack.addWidget(self.tsAnalysisWidget)
        self.setWidget(self.stack)
