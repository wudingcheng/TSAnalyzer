#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from qtpy.QtCore import QThread, Signal
import pyqtgraph as pg
# TODO: Implement DateAxisItem for proper time series X-axis
# import numpy as np # Might be needed for timestamp conversion


class TimeSeriesThread(QThread):
    sig_time_series_end = Signal()
    sig_log = Signal()

    def __init__(self, plot_widget, parent=None): # Changed figure to plot_widget
        super(TimeSeriesThread, self).__init__(parent=parent)
        self.plot_widget = plot_widget # Store plot_widget
        self._fitLines = []
        self.plots = [] # To store PlotItems

    def render(self, obj, task='ts'):
        self.task = 'ts' # Original logic: should this be self.task = task?
        self.obj = obj

    def renderReader(self):
        if self.obj is None:
            return
        self.plot_widget.clear()
        self.plots = [] # Clear previous plots
        # self.figure.suptitle(self.obj.name) # TODO: Set title on PlotItem if needed
        n = len(self.obj.columns)
        for i, col in enumerate(self.obj.columns):
            # TODO: Implement DateAxisItem for proper time series X-axis
            # For now, assuming self.obj.df.index are numerical or can be plotted directly
            # If self.obj.df.index are datetimes, they need conversion e.g., to timestamps
            # x_data = self.obj.df.index.values.astype(np.int64) // 10**9 if using datetime
            x_data = pg.ptime.mktime(self.obj.df.index.to_pydatetime()) # Convert datetime index to timestamps
            y_data = self.obj.df[col].values

            plot_item = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot_item.plot(x_data, y_data, pen='-', symbol='o', symbolPen=None, symbolBrush=None, symbolSize=2) # Basic styling
            plot_item.setLabel('left', col) # Set Y-axis label to column name
            if i < n - 1:
                plot_item.setLabel('bottom', text="") # Remove x-label for upper plots
            else:
                # TODO: Set proper date/time label for the last plot if using DateAxisItem
                plot_item.setLabel('bottom', text="Date")
            self.plots.append(plot_item)

        self.sig_time_series_end.emit()

    def renderFitOrResiduals(self, df, columns, task):
        self.df = df
        self.columns = columns
        self.task = task

    def _renderFit(self):
        # self.renderReader() # This would clear and redraw everything.
        # Instead, we assume plots are already created by renderReader and we add to them.
        # If renderReader is meant to be called, then self.plots should be managed accordingly.
        # For now, assuming we are adding fit lines to existing plots.
        if not self.plots or len(self.plots) != len(self.columns):
            # If plots don't exist or don't match, fall back to full render.
            # This might happen if renderFitOrResiduals is called before render.
            self.renderReader() # This will re-create self.plots based on self.obj

        self._fitLines = [] # Clear previous fit lines
        for i, col in enumerate(self.columns):
            if i < len(self.plots): # Ensure we don't go out of bounds
                plot_item = self.plots[i]
                # TODO: Implement DateAxisItem for proper time series X-axis
                # x_data = self.df.index.values.astype(np.int64) // 10**9 if using datetime
                x_data = pg.ptime.mktime(self.df.index.to_pydatetime()) # Convert datetime index to timestamps
                y_data = self.df[col].values
                line = plot_item.plot(x_data, y_data, pen='r', name=f"{col}_fit") # Added name for legend
                self._fitLines.append(line)
        # self.figure.canvas.draw_idle() # Not needed for pyqtgraph

    def _renderResiduals(self):
        self.plot_widget.clear()
        self.plots = []
        # self.figure.suptitle(self.obj.name) # TODO: Set title on PlotItem if needed
        n = len(self.columns)
        for i, col in enumerate(self.columns): # Assuming self.columns, but data comes from self.df
            # TODO: Implement DateAxisItem for proper time series X-axis
            # x_data = self.df.index.values.astype(np.int64) // 10**9 if using datetime
            x_data = pg.ptime.mktime(self.df.index.to_pydatetime())
            y_data = self.df[col].values

            plot_item = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot_item.plot(x_data, y_data, pen='-', symbol='o', symbolPen=None, symbolBrush=None, symbolSize=2)
            plot_item.setLabel('left', col)
            if i < n - 1:
                plot_item.setLabel('bottom', text="")
            else:
                plot_item.setLabel('bottom', text="Date")
            self.plots.append(plot_item)
        self.sig_time_series_end.emit()

    def _renderContinuous(self):
        # This method seems identical to _renderResiduals in structure, using self.df and self.columns
        # If self.obj is needed, it should be passed or set before calling.
        self.plot_widget.clear()
        self.plots = []
        # self.figure.suptitle(self.obj.name) # TODO: Set title on PlotItem if needed
        n = len(self.columns) # Assuming self.columns for iteration
        for i, col in enumerate(self.columns):
            # TODO: Implement DateAxisItem for proper time series X-axis
            # x_data = self.df.index.values.astype(np.int64) // 10**9 if using datetime
            x_data = pg.ptime.mktime(self.df.index.to_pydatetime())
            y_data = self.df[col].values

            plot_item = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot_item.plot(x_data, y_data, pen='-', symbol='o', symbolPen=None, symbolBrush=None, symbolSize=2)
            plot_item.setLabel('left', col)
            if i < n - 1:
                plot_item.setLabel('bottom', text="")
            else:
                plot_item.setLabel('bottom', text="Date")
            self.plots.append(plot_item)
        self.sig_time_series_end.emit()

    def start(self):
        if self.task in ('ts', 'clean'):
            self.renderReader()
        elif self.task == 'fit': # Changed to elif for clarity
            self._renderFit()
        elif self.task == 'residuals': # Changed to elif
            self._renderResiduals()
        elif self.task == 'continuous': # Changed to elif
            self._renderContinuous()
