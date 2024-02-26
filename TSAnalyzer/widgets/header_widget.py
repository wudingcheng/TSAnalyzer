#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import QTextCursor
from qtpy.uic import loadUi
from numpy import array, mean, std
from qtpy.compat import getopenfilenames

from ..utils import getIcon

import os
import re

date_dicts = {'y-m-d': '%Y-%m-%d',
              'ymd': '%Y%m%d',
              'hms': '%H%M%S',
              'year': '%Y',
              'month': '%m',
              'day': '%d',
              'hour': '%H',
              'minute': '%M',
              'second': '%S',
              'doy': '%j',
              'mjd': '', }


class TSHeaderThread(QThread):

    progressSignal = Signal(float, str)

    def __init__(self, parent=None):
        super(TSHeaderThread, self).__init__(parent=parent)

    def get_header(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            number_ratios = []
            for line in lines:
                temp = re.findall('\d', line)
                try:
                    number_ratios.append(
                        len(temp) * 1.0 / len(''.join(line.split())))
                except:
                    number_ratios.append(0)

            number_ratios = array(number_ratios)
            cretion = mean(number_ratios) - std(number_ratios)
            index = number_ratios > cretion
            try:
                return list(index).index(True)
            except:
                return 0

    def render(self, files, directory, header):
        self.files = files
        self.directory = directory
        self.header = header
        self.start()

    def run(self):
        files_count = len(self.files)
        for i, filename in enumerate(self.files):
            with open(filename, 'r') as f:
                lines = f.readlines()
                header_line = self.get_header(filename)
                content = self.header + ''.join(lines[header_line:])
            new_name = os.path.join(
                self.directory, os.path.split(filename)[1].split('.')[0] + '.dat')
            with open(new_name, 'w') as f:
                f.write(content)
            # self.done += 1
            # self.progressBar.setValue(self.done * 100.0 / self.cout)
            self.progressSignal.emit((i + 1) * 100.0 / files_count, filename)


class FileHeaderWidget(QWidget):

    def __init__(self, parent=None):
        super(FileHeaderWidget, self).__init__(parent=parent)
        ui = os.path.join(os.path.dirname(__file__),
                          "../resources/ui/header.ui")
        self.setWindowIcon(getIcon('icon'))
        loadUi(ui, self)
        self.thread = TSHeaderThread(self)
        self.thread.progressSignal.connect(self.sigOnWrite)
        self.addFilesButton.clicked.connect(self._click_addFilesButton)
        self.deleteButton.clicked.connect(self._click_deleteButton)
        self.filesListWidget.doubleClicked.connect(self._preview_file)
        self.writeButton.clicked.connect(self._click_writeButton)
        self.indexColEdit.editingFinished.connect(self._indexColEdit_finished)
        self.dirButton.clicked.connect(self._click_dirButton)
        self.consoleLabel.setVisible(False)
        self.consoleLabel.setText("")
        self.cont = None
        self.done = 0
        self.directory = None
        self.label_10.setVisible(False)
        self.indexFormatsEdit.setVisible(False)

    def _click_dirButton(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose directory for saving new file",
            "",
            QFileDialog.DontUseNativeDialog)
        if directory:
            self.dirEdit.setText(directory)
            self.directory = str(directory)

    def _click_addFilesButton(self):
        files = getopenfilenames(
            None,
            "Choose Time Series Files", '',
            'tseries (*.*)',
            None,
            QFileDialog.DontUseNativeDialog)[0]
        files = [i for i in files]
        items = []
        for index in range(self.filesListWidget.count()):
            items.append(self.filesListWidget.item(index).text())
        items = list(set(items + list(files)))
        self.filesListWidget.clear()
        self.filesListWidget.addItems(items)
        self.cont = self.filesListWidget.count()

    def _click_deleteButton(self):
        item = self.filesListWidget.currentRow()
        self.filesListWidget.takeItem(item)
        if len(self.filesListWidget.selectedItems()) == 0:
            self.previewEdit.clear()

    def _preview_file(self):
        self.previewEdit.clear()
        if self.filesListWidget.currentItem() is not None:
            filename = self.filesListWidget.currentItem().text()
            with open(filename, 'r') as f:
                self.previewEdit.appendPlainText(f.read())
                self.previewEdit.moveCursor(QTextCursor.Start)

    def _indexColEdit_finished(self):
        index_col = str(self.indexColEdit.text()).split()
        try:
            formats = ' '.join([date_dicts[i] for i in index_col])
        except Exception as ex:
            QMessageBox.critical(
                self,
                "Error Input", "Do not support %s key words" % str(ex),
                QMessageBox.Ok)
            return
        self.indexFormatsEdit.setText(formats)

    def _error_promopt(self, error):
        QMessageBox.critical(
            self, "Error Input",
            str(error),
            QMessageBox.Ok)
        return False

    def _get_input(self):
        str(self.unitEdit.text())
        float(self.scaleEdit.text())
        column_indexs = list(map(float, str(self.colIndexEdit.text()).split()))
        if len(column_indexs) == 0:
            return self._error_promopt("Columns not specified!")
        column_names = str(self.colNameEdit.text()).split()
        if len(column_indexs) != len(column_names):
            return self._error_promopt(
                'The numbers of column indexs and column names should be equal!')
        index_col = str(self.indexColEdit.text()).split()
        if len(list(set(index_col + column_names))) != len(column_names):
            return self._error_promopt(
                "Index columns should be subset of columns")
        return True

    def _click_writeButton(self):
        self._indexColEdit_finished()
        try:
            if not self._get_input():
                return
        except Exception as ex:
            QMessageBox.critical(self, "Error Input", str(ex),
                                 QMessageBox.Ok)
            return
        if self.directory is None:
            QMessageBox.critical(
                self,
                "Error Directory",
                "Please select the target directory.",
                QMessageBox.Ok)
            return
        header = ("# time_unit: {}\n"
                  "# unit: {}\n"
                  "# scale: {}\n"
                  "# column_names: {}\n"
                  "# columns_index: {}\n"
                  "# index_cols: {}\n"
                  "# index_formats: {}\n").format(
            str(self.timeUnitBox.currentText()),
            str(self.unitEdit.text()),
            str(self.scaleEdit.text()),
            str(self.colNameEdit.text()),
            str(self.colIndexEdit.text()),
            str(self.indexColEdit.text()),
            str(self.indexFormatsEdit.text()))
        self.consoleLabel.setVisible(True)
        files = []
        for index in range(self.filesListWidget.count()):
            files.append(self.filesListWidget.item(index).text())
        self.thread.render(files, self.directory, header)

    def sigOnWrite(self, progress, filename):
        self.progressBar.setValue(progress)
        self.consoleLabel.setText("{} completed!".format(filename))

    def sigOnWriteEnd(self):
        self.consoleLabel.setText("")
        self.consoleLabel.setVisible(False)
