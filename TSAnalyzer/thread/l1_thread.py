#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from qtpy.QtCore import QThread, Signal
from ..algorithms.l1extensive import l1wrapper
from ..models.reader import Reader
from copy import deepcopy

def l1Analysis4Reader(reader, params, logSignal):
    sigma = params.pop('sigma')
    discontinuities = []
    for col in reader.columns:
        logSignal.emit("L1: {} {}".format(reader.filename, col))
        ind = reader.df['{}_sigma'.format(col)] < sigma
        series = reader.df[ind][[reader.time_unit, col, '{}_sigma'.format(col)]]
        series.columns = ['t', 'y', 'dy']
        temp = l1wrapper(series, reader.name, **params)
        for i in temp:
            i.component = col
        discontinuities += temp
    return discontinuities

class TSL1Thread(QThread):
    sig_log = Signal(str)
    sig_error = Signal(str)
    sig_l1_end = Signal(list)

    def __init__(self, parent=None):
        super(TSL1Thread, self).__init__(parent=parent)

    def render(self, reader, parameters):
        self.reader = reader
        self.parameters = parameters

    def run(self):
        # sigma = self.parameters.pop('sigma')
        # discontinuities = []
        # for col in self.reader.columns:
        #     ind = self.reader.df['{}_sigma'.format(col)] < sigma
        #     series = self.reader.df[ind][[self.reader.time_unit, col]]
        #     series.columns = ['t', 'y']
        #     temp = l1wrapper(series, **self.parameters)
        #     for i in temp:
        #         i.component = col
        #     discontinuities += temp
        try:
            discontinuities = l1Analysis4Reader(self.reader, self.parameters, self.sig_log)
        except Exception as ex:
            discontinuities = []
            self.sig_error.emit(str(ex))
        self.sig_log.emit(
            "Finished detection, {} possible discontinuities have been found!".format(len(discontinuities)))
        self.sig_l1_end.emit(discontinuities)

class TSL1BatchThread(QThread):

    sig_log = Signal(str)
    sig_error = Signal(str)
    sig_l1Batch_end = Signal(dict)
    sig_l1Batch_progress = Signal(float)

    def __init__(self, parent=None):
        super(TSL1BatchThread, self).__init__(parent=parent)
        self.reader = Reader()
        self.results = {}

    def render(self, files, params):
        self.files = files
        self.params = params
        # self.start()
        self.sig_log.emit("{} files will be detected!".format(len(self.files)))
        self.sig_log.emit("Parameters: {}".format(self.params))

    def terminate(self):
        super(TSL1BatchThread, self).terminate()

    def run(self):
        results = {}
        failed = []
        n = len(self.files)
        for i, f in enumerate(self.files):
            params = deepcopy(self.params)
            self.sig_log.emit("Start {}".format(f))
            try:
                self.reader.readFile(f)
                results[self.reader.name] = l1Analysis4Reader(self.reader, params, self.sig_log)
            except Exception as ex:
                self.sig_error.emit("{} failed!".format(f))
                failed.append(f)
            self.sig_l1Batch_progress.emit((i + 1) / n)
        if len(failed) > 0:
            self.sig_error.emit("Following files failed:\n{}".format("\n".join(failed)))
        self.sig_l1Batch_end.emit(results)


