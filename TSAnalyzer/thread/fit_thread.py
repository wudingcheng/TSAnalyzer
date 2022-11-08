#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from qtpy.QtCore import QThread, Signal
from ..algorithms.fit import TSFit

import pandas as pd
import os


class TSOutliersThread(QThread):
    sig_log = Signal(str)
    sig_error = Signal(str)

    def __init__(self, parent):
        super(TSOutliersThread, self).__init__(parent=parent)

    def render(self, reader, offsetsHandler, parameters):
        self.reader = reader
        self.offsetsHandler = offsetsHandler
        self.parameters = parameters

    def run(self):
        for col in self.reader.columns:
            series = self.reader.df[[
                self.reader.time_unit, col, '{}_sigma'.format(col)]]
            series.columns = ['t', 'y', 'dy']
            self.sig_log.emit("Remove {} outliers.".format(col))
            try:
                tsfit = TSFit(series)
                self.parameters['lst']['discontinuities'] = self.offsetsHandler.getSiteComponentOffsets(
                    self.reader.name, col)
                series = tsfit.outliers(**self.parameters)
                self.reader.df[[col, '{}_sigma'.format(col)]] = series[[
                    'y', 'dy']]
            except Exception as ex:
                self.sig_error.emit(str(ex))


class TSFitThread(QThread):
    sig_log = Signal(str)
    sig_error = Signal(str)
    sig_fit_end = Signal(dict)

    def __init__(self, parent=None):
        super(TSFitThread, self).__init__(parent=parent)

    def render(self, reader, offsetsHandler, parameters):
        self.reader = reader
        self.offsetsHandler = offsetsHandler
        self.parameters = parameters

    def run(self):
        try:
            results = {}
            fit = []
            residuals = []
            continuous = []
            log = '{} Fit:\n'.format(self.reader.filename)
            for col in self.reader.columns:
                if '{}_sigma'.format(col) in self.reader.df.columns:
                    series = self.reader.df[
                        [self.reader.time_unit, col, '{}_sigma'.format(col)]]
                    series.columns = ['t', 'y', 'dy']
                else:
                    series = self.reader.df[[self.reader.time_unit, col]]
                    series.columns = ['t', 'y']
                tsfit = TSFit(series)
                self.parameters['discontinuities'] = self.offsetsHandler.getSiteComponentOffsets(
                    self.reader.name, col)
                results[col], _fit, conti = tsfit.fit(**self.parameters)
                
                residuals.append(pd.Series(tsfit.series['y'].values - _fit, name=col, index=tsfit.series.index))
                fit.append(
                    pd.Series(_fit, name=col, index=tsfit.series.index))
                continuous.append(pd.Series(conti, name=col, index=tsfit.series.index))
                log += results[col].summary2(
                    title='{} {}'.format(self.reader.name, col)).as_text()
            log = log.replace('\n', '<br>')
            self.sig_log.emit(log)
            fit = pd.concat(fit, axis=1)
            residuals = pd.concat(residuals, axis=1)
            continuous = pd.concat(continuous, axis=1)
            self.sig_fit_end.emit({'fit': fit, 'residuals': residuals, 'continuous': continuous})
        except Exception as ex:
            self.sig_error.emit(str(ex))


class TSFitBatchThread(QThread):

    sig_log = Signal(str)
    sig_fitBatch_error = Signal(str)
    sig_fitBatch_progress = Signal(float)

    def __init__(self, parent=None):
        super(TSFitBatchThread, self).__init__(parent=parent)

    def render(self, reader, files, handler, params):
        self.reader = reader
        self.files = files
        self.handler = handler
        self.params = params
        self.directory = self.params.pop('directory')
        self.makeDirectory()

    def makeDirectory(self):
        self.logDir = os.path.join(self.directory, 'log')
        if not os.path.isdir(self.logDir):
            os.mkdir(self.logDir)
        self.dataDir = os.path.join(self.directory, 'data')
        if not os.path.isdir(self.dataDir):
            os.mkdir(self.dataDir)
        # self.imgDir = os.path.join(self.directory, 'img')
        # if not os.path.isdir(self.imgDir):
        #     os.mkdir(self.imgDir)

    def _fitWrapper(self, filename):
        results = {}
        residuals = []
        continuous = []
        self.reader.readFile(filename)
        log = 'File: {}\n'.format(filename)
        for col in self.reader.columns:
            series = self.reader.df[[
                self.reader.time_unit, col, '{}_sigma'.format(col)]]
            series.columns = ['t', 'y', 'dy']
            tsfit = TSFit(series)
            self.params['discontinuities'] = self.handler.getSiteComponentOffsets(
                self.reader.name, col)
            results[col], _, conti = tsfit.fit(**self.params)
            residuals.append(
                pd.Series(results[col].resid, name=col, index=tsfit.series.index))
            
            continuous.append(pd.Series(conti, name=col, index=tsfit.series.index))
            log = results[col].summary(
                title='{} {}'.format(self.reader.name, col)).as_text()
        residuals = pd.concat(residuals, axis=1)
        continuous = pd.concat(continuous, axis=1)
        with open('{}/{}.log'.format(self.logDir, self.reader.name), 'w') as f:
            f.write(log)
        filename = '{}/{}_res.dat'.format(self.dataDir, self.reader.name)
        self.reader.saveTODAT(residuals, filename)
        filename = '{}/{}_continuous.dat'.format(self.dataDir, self.reader.name)
        self.reader.saveTODAT(continuous, filename)

    def run(self):
        n = len(self.files)
        for i, f in enumerate(self.files):
            self.sig_log.emit("{}".format(f))
            # try:
            self._fitWrapper(f)
            # except Exception as ex:
            #     self.sig_fitBatch_error.emit(ex)
            print((i + 1) * 100 / n)
            self.sig_fitBatch_progress.emit((i + 1) / n)

        self.sig_log.emit("End!")
