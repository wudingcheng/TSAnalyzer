import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.dates import date2num
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory
from PyQt4.QtCore import QThread, pyqtSignal

from TSModel import TSReader
from TSModel.TSOffsets import get_offsets


class TSBatchThread(QThread):

    plotSignal = pyqtSignal(str)
    plotProgressSignal = pyqtSignal(int, str)
    detrendSignal = pyqtSignal(str)
    detrendProgressSignal = pyqtSignal()

    def __init__(self):
        super(TSBatchThread, self).__init__()
        self.ts_reader = TSReader()

    def _outliers(self, filename, **kwargs):
        df = self.read_file(filename, interval=self.kwargs['interval'])
        self.ts_reader.df = df
        self.ts_reader.kwargs = kwargs
        results = self.ts_reader.outliers(**kwargs)
        sigma = results.get('sigma', None)
        iqr = results.get('iqr', None)
        if sigma is not None:
            df.ix[sigma] = np.nan
        if iqr is not None:
            df.ix[iqr] = np.nan
        if not os.path.isdir(kwargs['dir']):
            os.mkdir(kwargs['dir'])
        saved_name = os.path.join(kwargs['dir'],
                                  os.path.split(filename)[1][:4] + '_%s.neu' % kwargs['name'])
        self.ts_reader.write(df, saved_name)
        return saved_name

    def _detrend(self, filename, **kwargs):
        df = self.read_file(filename, interval=self.kwargs['interval'])
        self.ts_reader.df = df
        self.ts_reader.kwargs = kwargs
        results = self.ts_reader.fit(**kwargs)
        return results

    def _stacking(self, filenames, saved_name='stacking.neu'):
        dfs = []
        for f in filenames:
            dfs.append(self.read_file(f, interval=self.kwargs['interval']))
        cols = self.ts_reader.columns
        cme = []
        for col in cols:
            component = pd.concat([df[col] for df in dfs], axis=1)
            sigma = pd.concat([df['%s_sigma' % col] for df in dfs], axis=1)
            index = component.index
            ind = component.count(axis=1) > 3
            component = component[ind].fillna(0).as_matrix()
            sigma = sigma[ind].fillna(0).as_matrix()
            sigma_2 = sigma**2
            epsilon = np.nansum(component / sigma_2, axis=1) / np.nansum(1.0 / sigma_2, axis=1)
            cme.append(pd.Series(epsilon, index=index[ind]))
        cme = pd.concat(cme, axis=1)
        cme.columns = cols
        cme.insert(0, self.ts_reader.time_unit, 0.0)
        # cme.insert(0, dfs[-1].columns[0], 0.0)
        for col in cols:
            cme['%s_sigma' % col] = 0.0
        self.ts_reader.write(cme, saved_name)
        return cme

    def read_file(self, filename, interval=None):
        self.ts_reader.read_file(filename)
        df = self.ts_reader.df
        if interval is None:
            return df
        start, end = interval['all']
        ind = np.logical_and(df.index >= start, df.index <= end)
        df = df[ind]
        if interval.get(os.path.split(filename)[1][:4].lower(), None):
            start, end = interval[os.path.split(filename)[1][:4].lower()]
            ind = np.logical_and(df.index >= start, df.index <= end)
            df = df[~ind]
        return df

    def detrend(self, **kwargs):
        self.kwargs = kwargs
        filenames = kwargs['files']
        clean_files = []
        if kwargs['outliers']:
            self.detrendSignal.emit('Start removing outliers.')
            for f in filenames:
                outliers_dict = kwargs['outliers'].copy()
                if kwargs['detrend']:
                    outliers_dict['polys'] = kwargs['detrend']['polys']
                    outliers_dict['periods'] = kwargs['detrend']['periods']
                    outliers_dict['offsets'] = kwargs['detrend']['offsets'].get(
                        os.path.split(f)[1][:4].lower(), None)
                else:
                    outliers_dict.update({'polys': 1})
                clean_files.append(self._outliers(f, **outliers_dict))
                self.detrendSignal.emit('cleaned %s, saved in %s' % (f, clean_files[-1]))
                self.detrendProgressSignal.emit()
        else:
            clean_files = filenames
        residual_files = []
        if kwargs['detrend']:
            self.detrendSignal.emit("Start Detrending time series.")
            for filename in clean_files:
                detrend_dict = kwargs['detrend'].copy()
                detrend_dict['offsets'] = kwargs['detrend']['offsets'].get(
                    os.path.split(filename)[1][:4].lower(), None)
                results = self._detrend(filename, **detrend_dict)
                if not os.path.isdir(kwargs['detrend']['log']):
                    os.mkdir(kwargs['detrend']['log'])
                log = os.path.join(kwargs['detrend']['log'],
                                   os.path.split(filename)[1][:4] + '.log')
                with open(log, 'w') as f:
                    f.write(results['log'])
                if not os.path.isdir(kwargs['detrend']['dir']):
                    os.mkdir(kwargs['detrend']['dir'])
                residual_file = os.path.join(kwargs['detrend']['dir'], os.path.split(filename)[1][
                                             :4] + '_%s.neu' % kwargs['detrend']['name'])
                self.ts_reader.write(results['residual'], residual_file)
                self.detrendSignal.emit('detrend %s, saved in %s' % (filename, residual_file))
                self.detrendProgressSignal.emit()
                residual_files.append(residual_file)
        else:
            residual_files = clean_files
        if kwargs['cme']:
            if kwargs['cme']['method'] == 'Stacking':
                saved_name = os.path.join(kwargs['cme']['dir'], 'cme.neu')
                cme = self._stacking(residual_files, saved_name=saved_name)
                if kwargs['detrend']:
                    for f in residual_files:
                        self.ts_reader.read_file(f)
                        df = self.ts_reader.df
                        cols = df.columns.tolist()
                        df = df.subtract(cme, axis=1)
                        df = df[cols]
                        self.ts_reader.write(df, f)
                    kwargs['cme'] = False
                    kwargs['outliers'] = False
                    kwargs['files'] = clean_files
                    self.detrend(**kwargs)

    def plot(self, **kwargs):
        self.figure = Figure(figsize=(8, 6), dpi=kwargs['dpi'])
        FigureCanvas(self.figure)
        filenames = kwargs['files']
        for f in filenames:
            self.ts_reader.read_file(f)
            cols = self.ts_reader.columns
            df = self.ts_reader.df
            self.figure.clear()
            for i, c in enumerate(cols):
                ax = self.figure.add_subplot(len(cols), 1, 1 + i)
                ax.hold(True)
                ax.set_ylabel(c.upper() + ' (%s)' % self.ts_reader.unit, fontname='Microsoft Yahei')
                if kwargs.get('errorbar', False):
                    ax.errorbar(df.index, df[c], yerr=df['%s_sigma' % c],
                                fmt='ko', markersize=2)
                else:
                    ax.plot(df.index, df[c], 'ko', markersize=2)
            ax.set_xlabel('Date', fontname='Microsoft Yahei', fontsize='large')
            _, f = os.path.split(f)
            # offsets = get_offsets(f[:4].lower(), file=offsets)
            if kwargs.get('offsets', None):
                offsets = kwargs['offsets'][f[:4].lower()]
                if offsets is not None:
                    for date_str, components in offsets.iteritems():
                        date = datetime.strptime(date_str, "%Y%m%d")
                        for col, value in components.iteritems():
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
            self.figure.suptitle(f, fontsize='x-large', fontname='Microsoft Yahei')
            saved_filename = os.path.join(kwargs.get('dir', './'), '%s.%s' % (f, kwargs['format']))
            if saved_filename:
                self.figure.savefig(saved_filename, dpi=kwargs['dpi'])
            self.plotProgressSignal.emit(1, saved_filename)
            self.plotSignal.emit('Plot %s successfully!' % f)

    def render(self, **kwargs):
        self.kwargs = kwargs
        self.start()

    def run(self):
        task = self.kwargs['task']
        if task == 'plot':
            self.plot(**self.kwargs)
        if task == 'detrend':
            self.detrend(**self.kwargs)


if __name__ == '__main__':
    # filenames = ['Example/chum.neu', 'Example/CAND.sio.noamf_frame.pos']
    import glob
    filenames = glob.glob("../../TianShan/clean_neu/*.neu")
    # print filenames
    config = {'format': 'png', 'dpi': 300, 'files': filenames,
              "offsets": {}}
    batch = TSBatchThread()
    # batch.plot(**config)
    config = {'outliers': {
        'iqr_factor': 0, 'iqr_window': 365, 'sigma': [30, 30, 30],
        'dir': 'Example/clean', 'name': 'clean'},
        'cme': {'method': 'Stacking', 'dir': 'Example/cme'},
        'cme': False,
        'detrend': {
        'polys': 1, 'periods': [0.5, 1.0],
        'log': 'Example/log', 'dir': 'Example/residual', 'name': 'residual'},
        'files': filenames,
        'interval': None}
    # batch.kwargs['interval'] = None
    batch.detrend(**config)
    # ts_reader = TSReader()
    # ts_reader.read_file('Example/residual/tash_residual.neu')
    # df = ts_reader.df
    # col = df.columns.tolist()
    # ts_reader.read_file('Example/cme/cme.neu')
    # cme = ts_reader.df
    # print df.head()
    # print cme.head()
    # df = df.subtract(cme, axis=1)
    # df = df[col]
    # print df.columns
    # ts_reader.write(df, 'test.neu')
