#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import QDockWidget, QPlainTextEdit
from qtpy.QtCore import QCoreApplication
from qtpy.QtGui import QTextCursor
from datetime import datetime

def _(text, disambiguation=None, context='ConsoleDockWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)

class ConsoleDockWidget(QDockWidget):

    def __init__(self, parent=None):
        super(ConsoleDockWidget, self).__init__(parent=parent)
        self.setWindowTitle(_("Console"))
        self.__initWidgets()

    def __initWidgets(self):
        self.consoleEdit = QPlainTextEdit()
        self.setWidget(self.consoleEdit)

    def slotOnShowLog(self, s):
        s = "<font color='black'>({}) {}".format(str(datetime.now())[:-10], s)
        self._slotOnShowLog(s)

    def _slotOnShowLog(self, s):
        self.consoleEdit.appendHtml(s)
        self.consoleEdit.moveCursor(QTextCursor.End)

    def slotOnShowErrors(self, status):
        s = "<font color='red'>({}) {}</font>".format(str(datetime.now())[:-10], status)
        self._slotOnShowLog(s)
