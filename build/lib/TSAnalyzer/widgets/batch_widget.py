#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import QTextCursor
from qtpy.uic import loadUi
from qtpy.compat import getexistingdirectory
from datetime import datetime
import os

from ..thread.l1_thread import TSL1BatchThread
from ..thread.fit_thread import TSFitBatchThread
from ..models.reader import Reader
from ..utils import getIcon

class _BatchWidget(QWidget):

    def __init__(self, files, offsetsHandler, params, parent=None):
        super(_BatchWidget, self).__init__(parent=parent)
        ui = os.path.join(os.path.dirname(__file__), "../resources/ui/batch.ui")
        loadUi(ui, self)
        self.setWindowIcon(getIcon("icon"))
        self.files = files
        self.handler = offsetsHandler
        self.params = params

    def slotOnShowLog(self, s):
        s = "<font color='black'>({}) {}".format(str(datetime.now())[:-10], s)
        self._slotOnShowLog(s)

    def _slotOnShowLog(self, s):
        self.consoleEdit.appendHtml(s)
        self.consoleEdit.moveCursor(QTextCursor.End)

    def slotOnShowStatus(self, percentage):
        self.progressBar.setValue(percentage * 100)

    def slotOnShowErrors(self, status):
        s = "<font color='red'>({}) {}</font>".format(str(datetime.now())[:-10], status)
        self._slotOnShowLog(s)



class L1BatchWidget(_BatchWidget):

    sig_discontinuities_imported = Signal(dict)

    def __init__(self, files, offsetsHandler, params, parent=None):
        super(L1BatchWidget, self).__init__(files, offsetsHandler, params, parent=parent)
        self.setWindowTitle("TSAnalyzer L1 Detection Batch")
        self._canImport = False
        self.offsets = {}
        self.thread = TSL1BatchThread()
        self.thread.sig_log.connect(self.slotOnShowLog)
        self.thread.sig_error.connect(self.slotOnShowErrors)
        self.thread.sig_l1Batch_progress.connect(self.slotOnShowStatus)
        self.thread.sig_l1Batch_end.connect(self.slotOnEnd)
        self.thread.render(self.files, self.params)
        self.thread.started.connect(lambda: self.terminateButton.setEnabled(True))

    @property
    def canImport(self):
        return self._canImport

    @canImport.setter
    def canImport(self, flag):
        self._canImport = flag
        self.terminateButton.setEnabled(flag)
        if flag:
            self.terminateButton.setText("Import")
        else:
            self.terminateButton.setText("Terminate")

    def slotOnEnd(self, offsets):
        self.canImport = True
        self.offsets = offsets

    @Slot()
    def on_startButton_clicked(self):
        # print('clicked')
        self.canImport = False
        self.thread.start()

    @Slot()
    def on_terminateButton_clicked(self):
        if self.canImport:
            self.sig_discontinuities_imported.emit(self.offsets)
            for site, discontinuities in self.offsets.items():
                self.slotOnShowLog("{} {} discontinuities imported!".format(site, len(discontinuities)))
                self.handler.addDiscontinuities(site, discontinuities)
        else:
            self.thread.terminate()



class FitBatchWidget(_BatchWidget):

    def __init__(self, files, offsetsHandler, params, parent=None):
        super(FitBatchWidget, self).__init__(files, offsetsHandler, params, parent=parent)
        self.setWindowTitle("TSAnalyzer Fit Batch")
        self.dirButton = QPushButton("Directory")
        self.dirButton.clicked.connect(self.slotOndirButtonClicked)
        self.horizontalLayout.insertWidget(0, self.dirButton)
        self.directory = ""
        self.thread = TSFitBatchThread(self)
        self.thread.sig_log.connect(self.slotOnShowLog)
        self.thread.sig_fitBatch_error.connect(self.slotOnShowErrors)
        self.thread.sig_fitBatch_progress.connect(self.slotOnShowStatus)
        self.thread.finished.connect(lambda: self.terminateButton.setEnabled(False))
        self.reader = Reader()

        self.slotOnShowLog("{} files will be analyzed!".format(len(self.files)))
        self.slotOnShowLog("Parameters: {}".format(self.params))

    def slotOndirButtonClicked(self):
        self.directory = getexistingdirectory(self,
                                              "Select dir",
                                              "",
                                              QFileDialog.DontUseNativeDialog)
        if os.path.isdir(self.directory):
            self.slotOnShowLog("Results will be saved in {}".format(self.directory))


    @Slot()
    def on_startButton_clicked(self):
        if not os.path.isdir(self.directory):
            self.slotOnShowErrors("Please select directory!")
            return
        self.params['directory'] = self.directory
        self.thread.render(self.reader, self.files, self.handler, self.params)
        self.terminateButton.setEnabled(True)
        self.thread.start()

    @Slot()
    def on_terminateButton_clicked(self):
        # self.thread.terminate()
        self.thread.terminate()

