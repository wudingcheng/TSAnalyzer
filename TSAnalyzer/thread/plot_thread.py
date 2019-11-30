#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from qtpy.QtCore import QThread, Signal


class TimeSeriesThread(QThread):
    sig_time_series_end = Signal()
    sig_log = Signal()

    def __init__(self, figure, parent=None):
        super(TimeSeriesThread, self).__init__(parent=parent)
        self.figure = figure
        self._fitLines = []

    def render(self, obj, task='ts'):
        self.task = 'ts'
        self.obj = obj

    def renderReader(self):
        if self.obj is None:
            return
        self.figure.clear()
        self.figure.suptitle(self.obj.name)
        n = len(self.obj.columns)
        for i, col in enumerate(self.obj.columns):
            ax = self.figure.add_subplot(n, 1, i + 1)
            ax.plot(self.obj.df.index,
                    self.obj.df[col],
                    '.-',
                    linewidth=0.5,
                    markersize=2)
            if i < n - 1:
                ax.set_xlabel("")

        self.sig_time_series_end.emit()

    def renderFitOrResiduals(self, df, columns, task):
        self.df = df
        self.columns = columns
        self.task = task

    def _renderFit(self):
        self.renderReader()
        for i, col in enumerate(self.columns):
            ax = self.figure.axes[i]
            line, = ax.plot(self.df.index, self.df[col], '-r', linewidth=1)
            self._fitLines.append(line)
        self.figure.canvas.draw_idle()

    def _renderResiduals(self):
        self.figure.clear()
        n = len(self.columns)
        self.figure.suptitle(self.obj.name)
        for i, col in enumerate(self.obj.columns):
            ax = self.figure.add_subplot(n, 1, i + 1)
            ax.plot(self.df.index, self.df[col],
                    '.-', linewidth=0.5, markersize=2)
            if i < n - 1:
                ax.set_xlabel("")
        self.sig_time_series_end.emit()

    def _renderContinuous(self):
        self.figure.clear()
        n = len(self.columns)
        self.figure.suptitle(self.obj.name)
        for i, col in enumerate(self.obj.columns):
            ax = self.figure.add_subplot(n, 1, i + 1)
            ax.plot(self.df.index, self.df[col],
                    '.-', linewidth=0.5, markersize=2)
            if i < n - 1:
                ax.set_xlabel("")
        self.sig_time_series_end.emit()

    def start(self):
        if self.task in ('ts', 'clean'):
            self.renderReader()
        if self.task == 'fit':
            self._renderFit()
        if self.task == 'residuals':
            self._renderResiduals()
        if self.task == 'continuous':
            self._renderContinuous()
