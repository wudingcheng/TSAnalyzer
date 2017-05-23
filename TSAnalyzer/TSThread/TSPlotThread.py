from datetime import datetime, timedelta

from matplotlib.dates import date2num
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

# from PyQt4.QtCore import QThread, pyqtSignal
from qtpy.QtCore import QThread, Signal


class TSPlotThread(QThread):
    plotEndSignal = Signal(str)
    plotBreaksEnd = Signal(dict)
    plotTSEndSignal = Signal()

    def __init__(self, figure):
        super(TSPlotThread, self).__init__()
        self.figure = figure
        self.errors = None

    def plot(self, df, **kwargs):
        self.df = df
        self.kwargs = kwargs
        self.start()

    def plot_breaks(self):
        date_str = self.kwargs['date_str']
        components = self.kwargs["components"]
        cols = self.kwargs['cols']
        if date_str is None or components is None:
            return
        if len(self.figure.get_axes()) == 0:
            self.plot_ts()
        date = datetime.strptime(date_str, "%Y%m%d")
        temp = {}
        for col, value in components.items():
            ind = cols.index(col)
            ax = self.figure.get_axes()[ind]
            patch = None
            if value == 'eq':
                patch = ax.axvline(date, color='r')
            if value == 'ep':
                patch = ax.axvline(date, color='b')
            if value.startswith('eq exp'):
                trans = blended_transform_factory(ax.transData,
                                                  ax.transAxes)
                end = date + timedelta(int(value.split()[-1]))
                start = date2num(date)
                end = date2num(end)
                width = end - start
                patch = Rectangle((start, 0), width, 1,
                                  transform=trans,
                                  visible=True,
                                  facecolor='b',
                                  edgecolor='b',
                                  alpha=0.8)
                ax.add_patch(patch)
            if value.startswith('eq log'):
                trans = blended_transform_factory(ax.transData,
                                                  ax.transAxes)
                end = date + timedelta(int(value.split()[-1]))
                start = date2num(date)
                end = date2num(end)
                width = end - start
                patch = Rectangle((start, 0), width, 1,
                                  transform=trans,
                                  visible=True,
                                  facecolor='r',
                                  edgecolor='r',
                                  alpha=0.8)
                ax.add_patch(patch)
            if patch is not None:
                temp[col] = patch
        self.plotBreaksEnd.emit({date_str: temp})

    def plot_ts(self):
        cols = self.kwargs["cols"]
        errors = []
        self.figure.clear()
        for i, c in enumerate(cols):
            ax = self.figure.add_subplot(len(cols), 1, 1 + i)
            ax.set_ylabel('%s (%s)' % (c.upper(), self.kwargs['unit']))
            error = ax.errorbar(self.df.index, self.df[c], yerr=self.df['%s_sigma' % c],
                                fmt='ko', picker=3, markersize=3, capsize=3)
            errors.append(error)
            error[2][0].set_visible(self.kwargs.get('errorbar', False))
            error[1][1].set_visible(self.kwargs.get('errorbar', False))
            error[1][0].set_visible(self.kwargs.get('errorbar', False))
        self.figure.suptitle(self.kwargs.get('title', ''),
                             fontsize='x-large')
        self.errors = errors
        ax.set_xlabel('Date', fontsize='large')
        self.plotEndSignal.emit("plot %s successfully" % self.kwargs.get('title', '').lower())
        self.plotTSEndSignal.emit()

        fit = self.kwargs.get('fit', None)
        if fit is not None:
            for ax, c in zip(self.figure.get_axes(), cols):
                ax.plot(fit.index, fit[c], 'r', label='%s fit' % c, zorder=10)
                # self.plotEndSignal.emit("plot fit lines successfully")
        offsets = self.kwargs.get('offsets', None)
        if offsets:
            for key, value in offsets.items():
                self.kwargs['date_str'] = key
                # components = self.kwargs["components"]
                self.kwargs['components'] = value
                self.plot_breaks()

    def plot_errors(self):
        cols = self.kwargs['cols']
        axes = self.figure.get_axes()
        for ax, col in zip(axes, cols):
            ax.plot(self.df.index, self.df[col], self.kwargs['fmt'])

    def run(self):
        self.task = self.kwargs['task']
        if self.task == 'ts':
            self.plot_ts()
        if self.task == 'outliers':
            self.plot_errors()
        if self.task == 'breaks':
            self.plot_breaks()
        # if self.task == 'fit':
        #     self.plot_fit()
        self.figure.tight_layout()
        if len(self.kwargs["cols"]) == 1:
            ax = self.figure.get_axes()[0]
            ax.legend(loc='best')
        self.figure.subplots_adjust(hspace=0.1, top=0.95)
        self.figure.canvas.draw()

        # self.plotEndSignal.emit(self.errors)
