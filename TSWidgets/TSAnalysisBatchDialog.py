import json
import os
from datetime import datetime

from PyQt4.QtCore import SIGNAL, pyqtSlot
from PyQt4.QtGui import (QApplication, QDialog, QFileDialog, QIcon,
                         QMessageBox, QTextCursor)

from AnalysisBatchDialog import Ui_Dialog as AnalysisBatchDialog
from TSThread import TSBatchThread


class TSAnalysisBatchDialog(QDialog, AnalysisBatchDialog):
    def __init__(self, parent=None):
        super(TSAnalysisBatchDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.setTabOrder(self.sigmaEdit, self.iqrBox)
        self.setTabOrder(self.iqrBox, self.iqrWindowBox)
        self.setTabOrder(self.iqrWindowBox, self.outlierDirEdit)
        self.setTabOrder(self.outlierDirEdit, self.outlierDirButton)
        self.setTabOrder(self.outlierDirButton, self.outlierNameEdit)
        self.thread = TSBatchThread()
        self.thread.finished.connect(self.end)
        self.thread.detrendSignal.connect(self.display_information)
        self.thread.detrendProgressSignal.connect(self.progress)
        buttons = [self.outlierDirButton, self.cmeButton,
                   self.logDirButton, self.saveDirButton]
        edits = [self.outlierDirEdit, self.cmeEdit,
                 self.logDirEdit, self.saveDirEdit]
        for i in range(len(buttons)):
            self.connect(buttons[i], SIGNAL('clicked()'),
                         lambda i=i: self.click_dir_button(edits[i]))
            buttons[i].setIcon(QIcon(":/TSResource/images/directory"))
        self.stackingGroup.setVisible(False)
        self.cout = 0.0
        self.current = 0.0
        self.progressBar.setValue(0.0)
        self.selectButton.setIcon(QIcon(":/TSResource/images/add.png"))
        self.selectButton.setText("")
        self.offsetButton.setIcon(QIcon(":/TSResource/images/offset.png"))
        self.dialog = QFileDialog(self)

    def end(self):
        self.display_information("Finished")
        # self.progressBar.setValue(0.0)

    def progress(self):
        self.current += 1
        self.progressBar.setValue(self.current * 100 / self.cout)

    def _get_paramenters(self):
        paramenters = {'outliers': False, "cme": False, 'detrend': False}
        if self.outlierGroup.isChecked():
            sigma = map(float, str(self.sigmaEdit.text()).split())
            iqr = int(self.iqrBox.value())
            iqr_window = int(self.iqrWindowBox.value())
            save_dir = str(self.outlierDirEdit.text())
            name = str(self.outlierNameEdit.text())
            outliers = {'sigma': sigma, 'iqr_factor': iqr,
                        'iqr_window': iqr_window, 'dir': save_dir,
                        'name': name}
            paramenters['outliers'] = outliers
            self.cout += 1

        if self.stackingGroup.isChecked():
            method = str(self.cmeBox.currentText())
            cme_dir = str(self.cmeEdit.text())
            cme = {'method': method, 'dir': cme_dir}
            paramenters['cme'] = cme

        if self.analysisGroup.isChecked():
            polys = int(self.polyBox.value())
            periods = map(float, str(self.periodEdit.text()).split())
            log_dir = str(self.logDirEdit.text())
            save_dir = str(self.saveDirEdit.text())
            name = str(self.saveNameEdit.text())
            if str(self.offsetEdit.text()):
                with open(str(self.offsetEdit.text()), 'r') as f:
                    try:
                        offsets = json.loads(f.read())
                    except:
                        QMessageBox.critical(self, "Unsupport Offsets File Format",
                                             'cannot read %s' % str(self.offsetEdit.text()),
                                             QMessageBox.Ok)
                        return
            else:
                offsets = {}
            detrend = {'polys': polys, 'periods': periods, 'log': log_dir,
                       'dir': save_dir, 'name': name, 'offsets': offsets}
            paramenters['detrend'] = detrend
            self.cout += 1
        return paramenters

    def _parse_formats(self, temp):
        if len(temp[0]) == len(temp[1]):
            if len(temp[0]) == 8:
                temp = [i + '0000' for i in temp]
            elif len(temp[0]) == 12:
                temp = temp
        else:
            QMessageBox.critical(self, "Error Input",
                                 "%s Wrong Date formats" % ' '.join(temp),
                                 QMessageBox.Ok)
            return False
        return [datetime.strptime(i, '%Y%m%d%H%M%S') for i in temp]

    def _parse_timeEdit(self):
        txt = str(self.timeEdit.toPlainText())
        if len(txt) == 0:
            return None
        lines = [i for i in txt.split('\n') if i[0] != '#']
        if len(lines) == 0:
            return None
        temp = lines[0].split()
        temp = self._parse_formats(temp)
        if not temp:
            return None
        interval = {'all': temp}
        for i in lines[1:]:
            temp = i.split()
            site = temp[0].lower()
            temp = self._parse_formats(temp[1:])
            if not temp:
                continue
            interval[site] = temp
        return interval

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
        self.cout = 0.0
        self.current = 0.0
        self.progressBar.setValue(0.0)
        try:
            paramenters = self._get_paramenters()
        except Exception, ex:
            QMessageBox.critical(self, "Error Input", str(ex),
                                 QMessageBox.Ok)
            return
        interval = self._parse_timeEdit()
        paramenters['interval'] = interval
        paramenters['task'] = 'detrend'
        paramenters['files'] = items
        self.cout *= len(items)
        self.thread.render(**paramenters)

    @pyqtSlot()
    def on_offsetButton_clicked(self):
        filename = self.dialog.getOpenFileName(self, 'Choose Offsets file', '', self.tr('*.json'),
                                          None, QFileDialog.DontUseNativeDialog)
        filename = u"%s" % filename
        self.offsetEdit.setText(filename)

    def click_dir_button(self, edit):
        directory = self.dialog.getExistingDirectory(self, 'Choose', edit.text(),
                                                QFileDialog.DontUseNativeDialog)
        edit.setText(directory)

    @pyqtSlot()
    def on_selectButton_clicked(self):
        files = self.dialog.getOpenFileNames(self, "Choose Time Series Files", '',
                                        self.tr('tseries (*.neu *.tseries *.pos *dat)'),
                                        None, QFileDialog.DontUseNativeDialog)
        items = []
        for index in xrange(self.listWidget.count()):
            items.append(self.listWidget.item(index).text())
        items = list(set(items + list(files)))
        self.listWidget.clear()
        self.listWidget.addItems(items)
        self.countLabel.setText("Total: %d" % len(items))

    def on_listWidget_itemDoubleClicked(self):
        ind = self.listWidget.currentRow()
        reply = QMessageBox.question(self,
                                     'Delete',
                                     "Delete %s from list?" % self.listWidget.item(ind).text(),
                                     QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.listWidget.takeItem(ind)
            self.countLabel.setText("Total: %d" % self.listWidget.count())
        else:
            return

    @pyqtSlot()
    def on_deleteButton_clicked(self):
        self.listWidget.clear()
        self.countLabel.setText("Total: 0")

    def display_information(self, s):
        s = '>> (%s) %s' % (str(datetime.now())[:-10], s)
        self.consoleEdit.appendPlainText(s)
        self.consoleEdit.moveCursor(QTextCursor.End)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    m = TSAnalysisBatchDialog()
    m.show()
    app.exec_()
