import os
import re

from numpy import array, mean, std
from PyQt4.QtGui import QDialog, QFileDialog, QIcon, QMessageBox, QTextCursor

import TSResource.images
from HeaderDialog import Ui_Form as HeaderDialog

date_dicts = {'ymd': '%Y%m%d',
              'hms': '%H%M%S',
              'year': '%Y',
              'month': '%m',
              'day': '%d',
              'hour': '%H',
              'minute': '%M',
              'second': '%S',
              'doy': '%j',
              'mjd': '', }


class TSHeaderDialog(QDialog, HeaderDialog):
    def __init__(self, parent=None):
        super(TSHeaderDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle("TSAnalyzer - Header Tool")
        self.addFilesButton.clicked.connect(self._click_addFilesButton)
        self.addFilesButton.setIcon(QIcon(":/TSResource/images/add.png"))
        self.deleteButton.clicked.connect(self._click_deleteButton)
        self.filesListWidget.doubleClicked.connect(self._preview_file)
        self.writeButton.clicked.connect(self._click_writeButton)
        self.indexColEdit.editingFinished.connect(self._indexColEdit_finished)
        self.dirButton.clicked.connect(self._click_dirButton)
        self.consoleLabel.setVisible(False)
        self.consoleLabel.setText("")
        self.cout = None
        self.done = 0
        self.directory = None
        self.label_10.setVisible(False)
        self.indexFormatsEdit.setVisible(False)

    def get_header(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            number_ratios = []
            for i, line in enumerate(lines):
                temp = re.findall('\d', line)
                try:
                    number_ratios.append(len(temp) * 1.0 / len(''.join(line.split())))
                except:
                    number_ratios.append(0)

            number_ratios = array(number_ratios)
            cretion = mean(number_ratios) - std(number_ratios)
            index = number_ratios > cretion
            try:
                return list(index).index(True)
            except:
                return 0

    def _click_dirButton(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose directory for saving new file",
                                                     "", QFileDialog.DontUseNativeDialog)
        if directory:
            self.dirEdit.setText(directory)
            self.directory = str(directory)

    def _click_addFilesButton(self):
        dialog = QFileDialog(self)
        files = dialog.getOpenFileNames(None, "Choose Time Series Files", '',
                                        'tseries (*.*)', None, QFileDialog.DontUseNativeDialog)
        files = [i for i in files]
        items = []
        for index in xrange(self.filesListWidget.count()):
            items.append(self.filesListWidget.item(index).text())
        items = list(set(items + list(files)))
        self.filesListWidget.clear()
        self.filesListWidget.addItems(items)
        self.cout = self.filesListWidget.count()

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
        except Exception, ex:
            QMessageBox.critical(self, "Error Input", "Do not support %s key words" % str(ex),
                                 QMessageBox.Ok)
            return
        self.indexFormatsEdit.setText(formats)

    def _error_promopt(self, error):
        QMessageBox.critical(self, "Error Input", str(error),
                             QMessageBox.Ok)
        return False

    def _get_input(self):
        str(self.unitEdit.text())
        float(self.scaleEdit.text())
        column_indexs = map(float, str(self.colIndexEdit.text()).split())
        if len(column_indexs) == 0:
            return self._error_promopt("Columns not specified!")
        column_names = str(self.colNameEdit.text()).split()
        if len(column_indexs) != len(column_names):
            return self._error_promopt('The numbers of column indexs and column names should be equal!')
        index_col = str(self.indexColEdit.text()).split()
        if len(list(set(index_col + column_names))) != len(column_names):
            return self._error_promopt("Index columns should be subset of columns")
        return True

    def write_header(self, filename, header):
        with open(filename, 'r') as f:
            self.consoleLabel.setText('Appending Header to %s' % filename)
            lines = f.readlines()
            header_line = self.get_header(filename)
            content = header + ''.join(lines[header_line:])
        new_name = os.path.join(self.directory, os.path.split(filename)[1].split('.')[0] + '.dat')
        with open(new_name, 'w') as f:
            f.write(content)
        self.done += 1
        self.progressBar.setValue(self.done * 100.0 / self.cout)

    def _click_writeButton(self):
        self._indexColEdit_finished()
        try:
            if not self._get_input():
                return
        except Exception, ex:
            QMessageBox.critical(self, "Error Input", str(ex),
                                 QMessageBox.Ok)
            return
        if self.directory is None:
            QMessageBox.critical(self, "Error Directory", "Please select the target directory.",
                                 QMessageBox.Ok)
            return
        header = '''# time_unit: %s
# unit: %s
# scale: %s
# column_names: %s
# columns_index: %s
# index_cols: %s
# index_formats: %s\n''' % (str(self.timeUnitBox.currentText()),
                            str(self.unitEdit.text()),
                            str(self.scaleEdit.text()),
                            str(self.colNameEdit.text()),
                            str(self.colIndexEdit.text()),
                            str(self.indexColEdit.text()),
                            str(self.indexFormatsEdit.text()))
        self.consoleLabel.setVisible(True)
        for index in xrange(self.filesListWidget.count()):
            file = str(self.filesListWidget.item(index).text())
            self.write_header(file, header)
        self.done = 0
        self.consoleLabel.setText("")
        self.consoleLabel.setVisible(False)

# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     m = TSHeaderDialog()
#     m.show()
#     app.exec_()
