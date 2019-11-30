#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
import os
from qtpy.uic import loadUi


class TimeSeriesAnalysisWidget(QWidget):

    name = 'least squares'
    sig_outliers_clicked = Signal(dict)
    sig_fit_clicked = Signal(dict)
    sig_fit_batch = Signal(dict)
    sig_l1_clicked = Signal(dict)
    sig_l1_bacth = Signal(dict)
    sig_data_saved = Signal()
    sig_data_changed = Signal(str)

    def __init__(self, parent=None, reader=None):
        super(TimeSeriesAnalysisWidget, self).__init__(parent=parent)
        self.reader = reader
        ui = os.path.join(os.path.dirname(__file__), "../resources/ui/analysis_timeseries.ui")
        loadUi(ui, self)
        try:
            import cvxpy as cvx
            self.l1SolverCombo.addItems(cvx.installed_solvers())
        except ImportError:
            self.l1Group.setEnabled(False)

        self.dataCombo.currentTextChanged.connect(self.sig_data_changed.emit)

    def _getL1Parameters(self):
        lam = self.l1LambdaSpin.value()
        rho = self.l1RhoSpin.value()
        threshold = self.l1FValueSpin.value()
        solver = self.l1SolverCombo.currentText()
        return {'lam': lam,
                'rho': rho,
                'threshold': threshold,
                'solver': solver,
                'offset': self.l1OffsetCheck.isChecked(),
                'trendchange': self.l1TrendChangeCheck.isChecked()}

    def _getOutliersParameters(self):
        sigma = self.outliersSigmaSpin.value()
        iqr_factor = self.outliersIQRFactorSpin.value()
        iqr_window = self.outliersIQRWindowSpin.value()
        return {'sigma': sigma, 'iqr_factor': iqr_factor, 'iqr_window': iqr_window}

    def _getLeastSquaresParameters(self):
        poly = self.lstPolySpin.value()
        periods = self._edit2FloatList(self.lstPeriodsEdit)
        return {"polys": poly, "periods": periods}

    def _edit2FloatList(self, edit):
        return list(map(float, edit.text().split()))

    @Slot()
    def on_l1Button_clicked(self):
        l1 = self._getL1Parameters()
        l1.update(self._getLeastSquaresParameters())
        l1['sigma'] = self.outliersSigmaSpin.value()
        self.sig_l1_clicked.emit(l1)

    @Slot()
    def on_l1BatchButton_clicked(self):
        l1 = self._getL1Parameters()
        l1.update(self._getLeastSquaresParameters())
        l1['sigma'] = self.outliersSigmaSpin.value()
        self.sig_l1_bacth.emit(l1)

    @Slot()
    def on_outliersButton_clicked(self):
        outliers = self._getOutliersParameters()
        outliers['lst'] = self._getLeastSquaresParameters()
        self.sig_outliers_clicked.emit(outliers)

    @Slot()
    def on_lstButton_clicked(self):
        # print(self._getLeastSquaresParameters())
        parameters = self._getLeastSquaresParameters()
        self.sig_fit_clicked.emit(parameters)

    @Slot()
    def on_lstBatchButton_clicked(self):
        parameters = self._getLeastSquaresParameters()
        self.sig_fit_batch.emit(parameters)

    @Slot()
    def on_dataSaveButton_clicked(self):
        self.sig_data_saved.emit()

    def setDataWidgetVisible(self, visible):
        self.dataWidget.setVisible(visible)
