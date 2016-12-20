from datetime import datetime, timedelta

from PyQt4.QtCore import QDateTime
from PyQt4.QtGui import QDialog, QMessageBox

from DateDialog import Ui_Dialog as DateDialog
from TSDate import *


class TSDateWidget(QDialog, DateDialog):

    def __init__(self, parent=None):
        super(TSDateWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle("TSAnalyzer - Date Tool")
        self.mjd = 51544.5
        self.julday = 2451545
        self.demical_year = 2000.0
        self.doy = "2000-001"
        self.date = datetime(2000, 1, 1, 12)
        self.dateEdit.setDateTime(QDateTime(2000, 1, 1, 12, 0))

        self.conversionButton.clicked.connect(self._click_conversionButton)
        self.ydEdit.setInputMask("9999-999")
        self.dyEdit.setInputMask("9999.9999")
        self.mjdEdit.setValue(51544.5)
        self.juldayEdit.setInputMask("9999999")
        self.gpsweekEdit.setInputMask("99999")

        self.radios = [self.dateRadio, self.mjdRadio, self.juldayRadio,
                       self.dyRadio, self.ydRadio, self.gpsweekRadio]
        self.edits = [self.dateEdit, self.mjdEdit, self.juldayEdit,
                      self.dyEdit, self.ydEdit, self.gpsweekEdit]

        # for radio, edit in zip(self.radios, self.edits):
        #     if isinstance(radio, QDateEdit):
        #         continue
        #     else:
        #         edit.textChanged.connect(lambda: radio.setChecked(True))

    def _click_conversionButton(self):
        try:
            self._conversion()
        except Exception, ex:
            QMessageBox.critical(self, "Error Inputs", str(ex), QMessageBox.Ok)
            return

    def _conversion(self):
        for radio, edit in zip(self.radios, self.edits):
            if radio.isChecked():
                text = edit.text()
                if radio == self.dateRadio:
                    dt = map(int, text.split("-")) + [12]
                    date = datetime(*dt)
                    mjd = date2mjd(date)
                    self.mjdEdit.setValue(date2mjd(date))
                    self.juldayEdit.setText("%d" % mjd2julday(mjd))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    yd = date2year_doy(date)
                    yd_str = '%d-%03d' % (yd[0], yd[1])
                    self.ydEdit.setText("%s" % yd_str)
                    self.gpsweekEdit.setText("%d" % date2gpsweek(date))
                if radio == self.mjdRadio:
                    mjd = float(text)
                    date = mjd2date(mjd)
                    qdate = QDateTime(date.year, date.month,
                                      date.day, 12, 0, 0)
                    self.dateEdit.setDateTime(qdate)
                    self.juldayEdit.setText("%d" % mjd2julday(mjd))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    yd = date2year_doy(date)
                    yd_str = '%d-%03d' % (yd[0], yd[1])
                    self.ydEdit.setText("%s" % yd_str)
                    self.gpsweekEdit.setText("%d" % date2gpsweek(date))
                if radio == self.juldayRadio:
                    jd = int(text)
                    mjd = julday2mjd(jd) + 0.5
                    date = mjd2date(mjd)
                    qdate = QDateTime(date.year, date.month,
                                      date.day, 12, 0, 0)
                    self.dateEdit.setDateTime(qdate)
                    self.mjdEdit.setValue(date2mjd(date))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    yd = date2year_doy(date)
                    yd_str = '%d-%03d' % (yd[0], yd[1])
                    self.ydEdit.setText("%s" % yd_str)
                    self.gpsweekEdit.setText("%d" % date2gpsweek(date))
                if radio == self.dyRadio:
                    dy = float(text)
                    mjd = yearfraction2mjd(dy)
                    date = mjd2date(mjd)
                    qdate = QDateTime(date.year, date.month,
                                      date.day, 12, 0, 0)
                    self.dateEdit.setDateTime(qdate)
                    self.mjdEdit.setValue(date2mjd(date))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    yd = date2year_doy(date)
                    yd_str = '%d-%03d' % (yd[0], yd[1])
                    self.ydEdit.setText("%s" % yd_str)
                    self.gpsweekEdit.setText("%d" % date2gpsweek(date))
                if radio == self.ydRadio:
                    yd = map(int, str(text).split("-"))
                    if yd[1] == 0:
                        edit.setText('%d-00%d' % (yd[0], 1))
                        yd[1] = 1
                    # plus 12 hours
                    date = year_doy2date(*yd) + timedelta(hours=12)
                    mjd = date2mjd(date)
                    qdate = QDateTime(date.year, date.month,
                                      date.day, 12, 0, 0)
                    self.dateEdit.setDateTime(qdate)
                    self.mjdEdit.setValue(date2mjd(date))
                    self.juldayEdit.setText("%d" % mjd2julday(mjd))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    self.gpsweekEdit.setText("%d" % date2gpsweek(date))
                if radio == self.gpsweekRadio:
                    date = gpsweek2date(int(self.gpsweekEdit.text()))
                    mjd = date2mjd(date)
                    qdate = QDateTime(date.year, date.month,
                                      date.day, 12, 0, 0)
                    self.dateEdit.setDateTime(qdate)
                    self.mjdEdit.setValue(date2mjd(date))
                    self.juldayEdit.setText("%d" % mjd2julday(mjd))
                    self.dyEdit.setText("%.4f" % mjd2yearfraction(mjd))
                    yd = date2year_doy(date)
                    yd_str = '%d-%03d' % (yd[0], yd[1])
                    self.ydEdit.setText("%s" % yd_str)
