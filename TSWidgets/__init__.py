from .MainWindow import Ui_MainWindow as MainWindow
from .AboutDialog import Ui_aboutWidget as AboutDialog
from .OffsetDialog import Ui_Dialog as OffsetDialog
from .TSHeaderDialog import TSHeaderDialog
from .TSDateWidget import TSDateWidget
from .TSPlotBatchDialog import TSPlotBatchDialog
from .TSAnalysisBatchDialog import TSAnalysisBatchDialog
from .LogDialog import Ui_Dialog as LogDialog
from .NavigationToolBar import NavigationToolbar
from .TSToolBar import TSToolBar
from .SPToolBar import SPToolBar
from .TSSigsegDialog import TSSigsegDialog
from PyQt4.QtCore import pyqtSignal, QDate
from PyQt4.QtGui import QDialog, QTextCursor, QFileDialog
from datetime import datetime


class TSOffsetDialog(QDialog, OffsetDialog):

    JUMP_EDITOR_DONE = pyqtSignal(dict)
    JUMP_EDITOR_DELETE = pyqtSignal(dict)

    def __init__(self, parent=None, breaks='eq', col='north', date='20000102', tau=0):
        super(TSOffsetDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.breaks = breaks
        self.col = col
        self.date = datetime.strptime(date, "%Y%m%d")
        self.tau = tau
        self.dateEdit.setDate(QDate(self.date.year,
                                    self.date.month,
                                    self.date.day))

        if self.breaks == 'ep':
            self.offsetBox.setCurrentIndex(0)
            self.eqGroup.setVisible(False)
        else:
            self.eqGroup.setVisible(True)
            self.offsetBox.setCurrentIndex(1)
            if 'log' in self.breaks:
                self.logRadio.setChecked(True)
            if 'exp' in self.breaks:
                self.expRadio.setChecked(True)
        if 'exp' in self.breaks or 'log' in self.breaks:
            self.tauBox.setValue(self.tau)
        else:
            self.tauBox.setEnabled(False)

        self.offsetBox.currentIndexChanged.connect(lambda i: self.eqGroup.setVisible(i))
        self.cancelButton.clicked.connect(self._click_cancelButton)
        self.confirmButton.clicked.connect(self._click_confirmButton)
        self.eqRadio.clicked.connect(lambda i: self.tauBox.setEnabled(not i))
        self.expRadio.clicked.connect(lambda i: self.tauBox.setEnabled(i))
        self.logRadio.clicked.connect(lambda i: self.tauBox.setEnabled(i))

    def _click_cancelButton(self):
        self.JUMP_EDITOR_DELETE.emit({'delete': True,
                                      'col': self.col,
                                      'orign': self.date.strftime('%Y%m%d')})
        self.close()

    def _click_confirmButton(self):
        date = str(self.dateEdit.text().replace('-', ''))
        result = {}
        if self.offsetBox.currentIndex() == 0:
            result = {date: {self.col: 'ep'}}
        elif self.eqRadio.isChecked():
            result = {date: {self.col: 'eq'}}
        elif self.expRadio.isChecked():
            result = {date: {self.col: 'eq exp %d' % int(self.tauBox.value())}}
        elif self.logRadio.isChecked():
            result = {date: {self.col: 'eq log %d' % int(self.tauBox.value())}}
        self.JUMP_EDITOR_DONE.emit({'orign': self.date.strftime('%Y%m%d'),
                                    'col': self.col,
                                    'edit': result,
                                    'delete': False})
        self.close()


class TSLogDialog(QDialog, LogDialog):

    def __init__(self, parent=None, name=None, log=None):
        super(TSLogDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle("TSAnalyzer Log")
        if name:
            self.name = name
            self.logLabel.setText(name)
        if log:
            self.log = log
            self.logEdit.appendPlainText(log)
            self.logEdit.moveCursor(QTextCursor.End)
        self.saveButton.clicked.connect(self._save_log)
        self.cancelButton.clicked.connect(lambda: self.close())

    def _save_log(self):
        filename = QFileDialog.getSaveFileName(self, 'Save Log',
                                               './%s.log' % self.name, 'log')
        filename = str(filename)
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log)
            self.close()
