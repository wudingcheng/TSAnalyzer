#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from ..utils import makeAction
import os
from qtpy.compat import getopenfilenames, getsavefilename
from collections import OrderedDict


def _(text, disambiguation=None, context='FileDockWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class FileDockWidget(QDockWidget):
    sig_file_loaded = Signal(str)
    sig_file_removed = Signal(str)

    def __init__(self, parent=None):
        super(FileDockWidget, self).__init__(parent=parent)
        self.setAcceptDrops(True)
        # self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setWindowTitle(_("Time-Series File"))
        self.__initWidgets()
        self.__initActions()
        self.files = []
        self.enableActions(False)
        self.__initSignals()

    def __initWidgets(self):
        self.filesWidget = QListWidget()
        self.filesWidget.setSortingEnabled(True)
        self.setWidget(self.filesWidget)

        self.menu = QMenu(self)

    def __initSignals(self):
        self.filesWidget.currentTextChanged.connect(self.slotOnCurrentTextChanged)
        self.filesWidget.itemDoubleClicked.connect(self.slotOnLoadFile)

    def enableActions(self, flag):
        self.actions['timeseries.remove'].setEnabled(flag)
        self.actions['timeseries.load'].setEnabled(flag)
        self.actions['timeseries.export'].setEnabled(flag)
        self.actions['timeseries.clear'].setEnabled(flag)

    def slotOnCurrentTextChanged(self, item):
        self.enableActions(True)
        self.actions['timeseries.remove'].setText("Remove {}".format(item))
        self.actions['timeseries.load'].setText("Load {}".format(item))

    def addFiles(self, files):
        self.files += list(files)
        self.files = sorted(list(set(self.files)))
        self._updateFilesWidget()

    def _updateFilesWidget(self):
        self.filesWidget.clear()
        self._files = {}
        for f in self.files:
            path, name = os.path.split(f)
            item = QListWidgetItem(name)
            item.setToolTip(f)
            self.filesWidget.addItem(item)
            self._files[f] = item

    def __initActions(self):
        _actions = [
            (self, _('Import Time-Series Files'), _('Import time-series files'),
             self.slotOnImportFiles, 'timeseries.files', None, False),
            None,
            (self, _('Load Time-Series File'), _('Load time-series file'),
             self.slotOnLoadFile, 'timeseries.load', None, False),
            # (self, _('Load next time-series file'), _('Load next time-series file'),
            #  lambda: self.slotOnNext(1), 'timeseries.next', False),
            None,
            (self, _('Remove selected file'), _('Remove'),
             self.slotOnRemoveFile, 'timeseries.remove', None, False),
            (self, _('Clear all files'), _('Clear'),
             self.slotOnClearFiles, 'timeseries.clear', None, False),
            (self, _('Export time series files into text file'), _("Export all time-series filename"),
             self.slotOnExportFilenames, 'timeseries.export', None, False)
        ]
        self.actions = OrderedDict()
        for act in _actions:
            if act is not None:
                a = makeAction(*act)
                # self.addAction(a)
                self.actions[act[-3]] = a
                self.menu.addAction(a)
            else:
                self.menu.addSeparator()

    def slotOnImportFiles(self):
        files = getopenfilenames(self,
                                 _("Choose Time Series Files"),
                                 '',
                                 _('tseries (*.dat *.neu *.tseries *.pos)'),
                                 None,
                                 QFileDialog.DontUseNativeDialog)[0]
        self.addFiles(files)
        if len(files) == 1:
            item = self._files[files[0]]
            self.filesWidget.setCurrentItem(item)
            # ind = self.files.index(files[0])
            # self.filesWidget.setCurrentRow(self.files.index(files[0]))
            self.slotOnLoadFile()

    def slotOnLoadFile(self):
        f = self.filesWidget.currentItem().toolTip()
        self.sig_file_loaded.emit(f)

    # def slotOnNext(self, ind):
    #     row = self.filesWidget.currentRow()
    #     row += ind
    #     row = len(self.files) if row < 0 else row
    #     row = 0 if row > len(self.files) else row
    #     self.filesWidget.setCurrentRow(row)
    #     self.slotOnLoadFile()

    def slotOnRemoveFile(self):
        ind = self.filesWidget.currentRow()
        if ind > -1:
            self.sig_file_removed.emit(self.files[ind])
            self.filesWidget.takeItem(ind)
            self.files.pop(ind)
        if len(self.files) == 0:
            self.enableActions(False)

    def slotOnClearFiles(self):
        self.files = []
        self._updateFilesWidget()
        self.enableActions(False)
        self.sig_file_removed.emit("")

    def slotOnExportFilenames(self):
        filename = getsavefilename(self,
                                   _("Record all time-series filenames"),
                                   'files.dat',
                                   _('list (*.list)'),
                                   None,
                                   QFileDialog.DontUseNativeDialog)[0]
        if filename:
            with open(filename, 'w') as f:
                f.write("\n".join(self.files))

    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(FileDockWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(FileDockWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                print(url)
