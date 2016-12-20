import json
from datetime import datetime

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import (QApplication, QDialog, QFileDialog, QIcon,
                         QMessageBox, QPixmap, QTextCursor)

from FigureBatchDialog import Ui_Dialog as FigureBatchDialog
from TSThread import TSBatchThread


class TSPlotBatchDialog(QDialog, FigureBatchDialog):

    def __init__(self, parent=None):
        super(TSPlotBatchDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.thread = TSBatchThread()
        self.count = 0.0
        self.imageLabel.setVisible(False)
        self.selectButton.setIcon(QIcon(":/TSResource/images/add.png"))
        self.selectButton.setText("")
        self.saveDirButton.setIcon(QIcon(":/TSResource/images/directory"))
        self.offsetsButton.setIcon(QIcon(":/TSResource/images/offset.png"))

    @pyqtSlot()
    def on_selectButton_clicked(self):
        dialog = QFileDialog(self)
        files = dialog.getOpenFileNames(self, "Choose Time Series Files", '',
                                        self.tr('tseries (*.neu *.tseries *.pos *dat)'),
                                        None, QFileDialog.DontUseNativeDialog)
        items = []
        for index in xrange(self.listWidget.count()):
            items.append(self.listWidget.item(index).text())
        items = list(set(items + list(files)))
        self.listWidget.clear()
        self.listWidget.addItems(items)
        self.countLabel.setText("Total: %d" % len(items))

    @pyqtSlot()
    def on_offsetsButton_clicked(self):
        dialog = QFileDialog(self)
        filename = dialog.getOpenFileName(self, 'Choose Offsets file',
                                          '', self.tr('*.json'),
                                          None, QFileDialog.DontUseNativeDialog)
        filename = u"%s" % filename
        self.offsetsEdit.setText(filename)

    @pyqtSlot()
    def on_saveDirButton_clicked(self):
        dialog = QFileDialog(self)
        directory = dialog.getExistingDirectory(self, 'Choose', '', QFileDialog.DontUseNativeDialog)
        self.dirEdit.setText(directory)

    @pyqtSlot()
    def on_batchButton_clicked(self):
        items = []
        for index in xrange(self.listWidget.count()):
            items.append(str(self.listWidget.item(index).text()))
        if len(items) == 0:
            QMessageBox.critical(self, "No Files",
                                 'Please input files.',
                                 QMessageBox.Ok)
            return
        if str(self.offsetsEdit.text()):
            with open(str(self.offsetsEdit.text()), 'r') as f:
                try:
                    offsets = json.loads(f.read())
                except:
                    QMessageBox.critical(self, "Unsupport Offsets File Format",
                                         'cannot read %s' % str(self.offsetsEdit.text()),
                                         QMessageBox.Ok)
                    return
        else:
            offsets = {}
        if str(self.dirEdit.text()) == '':
            QMessageBox.critical(self, "Empty Images output directory",
                                 'Please input images directory.',
                                 QMessageBox.Ok)
            return
        config = {'format': str(self.comboBox.currentText()),
                  'dpi': int(self.dpiBox.value()),
                  'errorbar': self.errorBarCheck.isChecked(),
                  'offsets': offsets,
                  'dir': str(self.dirEdit.text()),
                  'files': items,
                  'task': 'plot'}
        self.thread.plotSignal.connect(self.display_information)
        self.thread.plotProgressSignal.connect(self.progress)
        self.thread.finished.connect(self.end)
        self.thread.render(**config)

    def progress(self, i, image_file):
        self.count += i
        pix = QPixmap(image_file)
        # pix.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
        self.imageLabel.setScaledContents(True)
        self.progressBar.setValue(self.count * 100 / self.listWidget.count())
        self.imageLabel.setVisible(True)
        self.imageLabel.setPixmap(pix)

    def end(self):
        self.imageLabel.setVisible(False)
        self.progressBar.setValue(0.0)

    def display_information(self, s):
        s = '>> (%s) %s' % (str(datetime.now())[:-10], s)
        self.consoleEdit.appendPlainText(s)
        self.consoleEdit.moveCursor(QTextCursor.End)
