# encoding: utf-8
# author: WU Dingcheng

from __future__ import division, absolute_import, print_function

import os

import numpy as np
import pandas as pd

try:
    from PyQt4.QtCore import QThread, pyqtSignal
except ImportError:
    from PyQt5.QtCore import QThread, pyqtSignal

from ..TSDate import date2yearfraction, yearfraction2date, mjd2date
from .TSFit import TSFit
from .TSOffsets import offset_to_fit


class TSReader(QThread):
    outlierEndSignal = pyqtSignal(dict)
    fitEndSignal = pyqtSignal(dict)

    def __init__(self):
        super(TSReader, self).__init__()
        self.sampling = None
        self.freq = None
        self.evenly = True
        self.name = None
        self.unit = 'mm'
        self.time_unit = None
        self.filename = None
        self.cols = None
        self.columns = None

        self._parser_dates = False
        self._date_parser = None
        self.skiprows = 0
        self.scale = 1.0
        self.df = None
        self.freq = 'D'

    def read_header(self):
        if self.filename is None:
            return
        name = None
        col_names = None
        col_indexs = None
        index = None
        formats = None
        support_time_units = ['years', 'days']
        time_unit = 'years'
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("# name"):
                    name = line.strip().split()[-1]
                if line.startswith("# column_names"):
                    col_names = line.strip().split()[2:]
                if line.startswith("# columns_index"):
                    col_indexs = list(map(int, line.strip().split()[2:]))
                if line.startswith("# index_cols"):
                    index = line.strip().split()[2:]
                if line.startswith("# index_formats"):
                    formats = " ".join(line.strip().split()[2:])
                if line.startswith("# unit"):
                    self.unit = line.strip().split()[-1]
                if line.startswith("# scale"):
                    self.scale = float(line.strip().split()[-1])
                if line.startswith("# time_unit"):
                    time_unit = line.strip().split()[-1]
        if time_unit in support_time_units:
            self.time_unit = time_unit
        if index is None or self.time_unit is None:
            return
        filter_columns = ['year', 'month', 'day', 'hour', 'minute', 'seconds',
                          'doy', 'ymd', 'hms', 'mjd']
        self.columns = [
            i for i in col_names if i not in filter_columns and 'sigma' not in i]
        self.columns = [i for i in self.columns if i not in support_time_units]
        if name is None:
            self.name = os.path.split(self.filename)[1][: 4].upper()
        else:
            self.name = name
        self.cols = dict(zip(col_indexs, col_names))
        if index == ['mjd']:
            self._read_mjd(index='mjd')
            return
        self._parser_dates = {'datetime': index}
        self._date_parser = lambda x: pd.datetime.strptime(x, formats)

    def _interploate_time_column(self):
        t = self.df[self.time_unit].interpolate(method='linear')
        self.df[self.time_unit] = t

    def _infer_freq(self, index):
        jds = index.to_julian_date()
        sampling = min(np.diff(jds))
        self.sampling = sampling

        if self.sampling >= 1:
            self.freq = 'D'

    def _read_mjd(self, index='mjd'):
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            self.filename,
            header=None,
            sep="\s+",
            comment='#',
            names=names,
            usecols=cols,
            skiprows=self.skiprows)
        timeindex = list(map(mjd2date, self.df['mjd']))
        del self.df['mjd']
        self.df.index = timeindex

    def _read_tseries(self):
        self.name = os.path.split(self.filename)[1][: 4].upper()
        self.unit = 'mm'
        self.scale = 1000
        self.time_unit = 'years'
        self.columns = ['north', 'east', 'up']
        self.cols = {0: 'years', 1: 'east', 2: 'north', 3: 'up',
                     4: 'east_sigma', 5: 'north_sigma', 6: 'up_sigma',
                     11: 'year', 12: 'month', 13: 'day', 14: 'hour', 15: 'minute', 16: 'seconds'}
        # self._parser_dates = [11, 12, 13, 14, ...] # which is not right
        self._parser_dates = {'datetime': [
            'year', 'month', 'day', 'hour', 'minute', 'seconds']}
        self._date_parser = lambda x: pd.datetime.strptime(
            x, '%Y %m %d %H %M %S')
        self._read_file()

    def _read_neu(self):
        with open(self.filename, 'r') as f:
            # print 'column_names' in f.read()
            if 'column_names' in f.read():
                # print 'read_neu'
                self._read_default()
                return
        self.name = os.path.split(self.filename)[1][: 4].upper()
        self.unit = 'mm'
        self.scale = 1000
        self.time_unit = 'years'
        self.columns = ['north', 'east', 'up']
        self.cols = {0: 'years', 1: 'north', 2: 'east', 3: 'up',
                     4: 'north_sigma', 5: 'east_sigma', 6: 'up_sigma'}
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(self.filename, header=None, sep="\s+", comment='#',
                              names=names, usecols=cols)
        time_index = [yearfraction2date(i) for i in self.df.years]
        self.df.index = time_index

    def _read_pos(self):
        self.unit = 'mm'
        self.scale = 1000
        self.time_unit = 'years'
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'ID' in line:
                    self.name = line.split(':')[1].strip()
                if line.startswith('*YYYYMMDD'):
                    self.skiprows = i + 1
                    break
                if line.startswith(' '):
                    self.skiprows = i
                    break
        self.columns = ['north', 'east', 'up']
        self.cols = {0: 'ymd', 1: 'hms', 15: 'north', 16: 'east', 17: 'up',
                     18: 'north_sigma', 19: 'east_sigma', 20: 'up_sigma'}
        self._date_parser = lambda x: pd.datetime.strptime(x, '%Y%m%d %H%M%S')
        self._parser_dates = {'datetime': ['ymd', 'hms']}
        self._read_file()
        dys = date2yearfraction(list(self.df.index))
        self.df.insert(0, self.time_unit, dys)

    def _read_file(self):
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(self.filename,
                              header=None,
                              sep="\s+",
                              comment='#',
                              names=names,
                              usecols=cols,
                              index_col="datetime",
                              parse_dates=self._parser_dates,
                              date_parser=self._date_parser,
                              skiprows=self.skiprows)

    def _read_default(self):
        self.read_header()
        if self.df is None:
            self._read_file()
        if self.time_unit == 'years':
            dys = date2yearfraction(list(self.df.index))
        if self.time_unit == 'days':
            dys = self.df.index.to_julian_date()
        self.df = self.df[self.df.columns].apply(pd.to_numeric)
        self.df.insert(0, self.time_unit, dys)

    def read_file(self, filename):
        self.df = None
        self.filename = filename
        formats = self.filename.split('.')[-1]
        # self._read_default()
        try:
            read_func = getattr(self, '_read_%s' % formats)
            read_func()
        except Exception as ex:
            try:
                self._read_default()
            except Exception as ex:
                print(ex)
                return
        if self.df is None:
            return
        self._infer_freq(self.df.index)
        self.df.resample(self.freq)
        self._interploate_time_column()
        if self.scale > 1:
            self.df[self.df.columns[1:]] = self.df[
                self.df.columns[1:]].apply(lambda i: i * self.scale)
        for col in self.columns:
            if '%s_sigma' % col not in self.df.columns:
                self.df['%s_sigma' % col] = 1

    def interpolate(self, df, method='mean', order=3):
        if method != 'mean':
            df[self.columns] = df[self.columns].interpolate(
                method=method, order=order)
        df = self.df.fillna(self.df.mean)
        return df

    def outliers(self, **kwargs):
        sigmas = kwargs.get('sigma', None)
        print(kwargs)
        outliers = {}
        if sigmas:
            sigmas = sigmas * 3 if len(sigmas) == 1 else sigmas
            inds = []
            for sigma, col in zip(sigmas, self.columns):
                ind = self.df['%s_sigma' % col] > sigma
                inds.append(ind)
            ind = np.logical_or.reduce(np.array(inds))
            # ind = np.logical_or(inds[0], np.logical_or(inds[1], inds[2]))
            sigma_error_index = self.df.index[ind]
            # self.df.ix[sigma_error_index] = np.nan
            outliers['sigma'] = sigma_error_index
        iqr_factor = kwargs.get('iqr_factor', None)
        if iqr_factor:
            window = kwargs['iqr_window']
            inds = []
            results = self.fit(**kwargs)
            residual_df = results['residual']
            residual_df.resample(self.freq)
            self.interpolate(residual_df)
            for col in self.columns:
                residual = residual_df[col]
                median = pd.rolling_median(residual, window)
                q75 = pd.rolling_quantile(residual, window, 0.75)
                q25 = pd.rolling_quantile(residual, window, 0.25)
                qrange = iqr_factor * (q75 - q25)
                low = median - qrange
                high = median + qrange
                ind = np.logical_or(
                    residual.values < low.values, residual.values > high.values)
                ind2 = (residual - residual.mean()
                        ).abs() > iqr_factor * residual.std()
                ind = np.logical_or(ind, ind2)
                inds.append(ind)
            # ind = np.logical_or(inds[0], np.logical_or(inds[1], inds[2]))
            ind = np.logical_or.reduce(np.array(inds))

            iqr_error_index = residual_df.index[ind]
            outliers['iqr'] = iqr_error_index
        return outliers

    def fit(self, **kwargs):
        kwargs_copy = kwargs.copy()
        print(self.df.head())
        print(self.time_unit)
        t = self.df[self.time_unit].values
        print('t')
        print(t)
        t_contiuous = self.df[self.time_unit].interpolate(method='linear')
        ind = self.df.index[self.df[self.columns[0]].notnull()]
        fit_df = {}
        residuals_df = {}
        results = {}
        continuous_df = {}
        for col in self.columns:
            offsets_dict = kwargs_copy.get('offsets', None)
            offsets = []
            psdecays = []
            if offsets_dict is not None:
                offset_dates, psdecay_dates = offset_to_fit(
                    offsets_dict, component=col)
                for i in offset_dates:
                    date_index = self.df.index.searchsorted(i)
                    # offsets.append(self.df.ix[date_index][self.time_unit])
                    offsets.append(t_contiuous[date_index])
                for i in psdecay_dates:
                    start, end = self.df.index.searchsorted(
                        i[0]), self.df.index.searchsorted(i[1])
                    # start = self.df.ix[start][self.time_unit]
                    # end = self.df.ix[end][self.time_unit]
                    start = t_contiuous[start]
                    end = t_contiuous[end]
                    psdecays.append([start, end, i[2]])
            y = self.df[col].values
            dy = self.df['%s_sigma' % col].values
            tsfit = TSFit(t, y, cov=dy)
            temp = tsfit.ts_fit(offsets=offsets, psdecays=psdecays,
                                periods=kwargs_copy['periods'],
                                polys=kwargs_copy['polys'], full=True)
            fit_df[col] = temp['fit']
            residuals_df[col] = temp['v']
            continuous_df[col] = temp['continuous']
            temp.pop('fit')
            temp.pop('v')
            results[col] = temp
        fit_df = pd.DataFrame(fit_df).set_index(ind)
        residuals_df = pd.DataFrame(residuals_df).set_index(ind)
        continuous_df = pd.DataFrame(continuous_df).set_index(ind)
        fit_df.insert(0, self.time_unit, self.df[self.time_unit])
        residuals_df.insert(0, self.time_unit, self.df[self.time_unit])
        continuous_df.insert(0, self.time_unit, self.df[self.time_unit])
        for col in self.columns:
            residuals_df['%s_sigma' % col] = self.df['%s_sigma' % col]
            fit_df['%s_sigma' % col] = self.df['%s_sigma' % col]
            continuous_df['%s_sigma' % col] = self.df['%s_sigma' % col]
        # try:
        log = self.log_detrend(results, kwargs_copy.get('offsets', None))
        # except Exception as ex:
        #     print ex
        #     log = ''
        return {'results': results, 'log': log,
                'fit': fit_df, 'residual': residuals_df,
                'continuous': continuous_df}

    def log_detrend(self, solves, offsets):
        output = 'Least suqare fit \nEpochs: %d' % (self.df.ix[:, 1].count())
        for c in self.columns:
            solve = solves[c]
            output += '\n'
            i = 1
            output += '%s component:\n WRMS: %f %s, NRMS: %.2f\n' % \
                      (c.title(), solve['wrms'], self.unit, solve['nrms'])
            p, psigma = solve['p'], solve['sigma_x']
            output += '%s linear %f +- %f %s/yr \n' % (
                c.title(), p[i], psigma[i], self.unit)
            i += 1
            if solve['polys'] > 1:
                for j in range(2, solve['polys'] + 1):
                    output += '%s t**%d %f +- %f %s/yr**%d\n' % (
                        c.title(), j, p[i], psigma[i], self.unit, j)
                    i += 1
            periods = solve['periods']
            if periods is not None:
                for period in periods:
                    output += '%s %.1f %s cycle sin: %f +- %f %s \n' \
                        % (c.title(), period, self.time_unit,
                           p[i], psigma[i], self.unit)
                    i += 1
                    output += '%s %.1f %s cycle cos: %f +- %f %s \n' \
                        % (c.title(), period, self.time_unit, p[i],
                           psigma[i], self.unit)
                    i += 1
            if offsets:
                offsets = self.kwargs['offsets']
                for date_str, components in offsets.items():
                    date = pd.datetime.strptime(date_str, "%Y%m%d")
                    if pd.to_datetime(self.df.index.values[0]) >= date:
                        continue
                    if components.get(c, None):
                        if components[c] == 'ep':
                            output += '%s Equipment  offset : ' % c.title()
                            output += '%f +- %f %s at %s \n' % \
                                      (p[i], psigma[i], self.unit, date_str)
                            i += 1
                        if components[c] == 'eq':
                            output += '%s Earthquake offset : ' % c.title()
                            output += '%f +- %f %s at %s \n' % \
                                      (p[i], psigma[i], self.unit, date_str)

                            i += 1
                        if 'exp' in components[c]:
                            tau = int(components[c].split()[-1])
                            output += '%s %s ' % ("Earthquake Exp", date_str)
                            output += 'Tau days %d, %f +- %f %s \n' \
                                % (tau, p[i], psigma[i], self.unit)
                            i += 1
                        if 'log' in components[c]:
                            tau = int(components[c].split()[-1])
                            output += '%s %s ' % ("Earthquake Log", date_str)
                            output += 'Tau days %d, %f +- %f %s \n' \
                                % (tau, p[i], psigma[i], self.unit)
                            i += 1
        return output

    def render(self, **kwargs):
        self.task = kwargs.get('task', None)
        self.kwargs = kwargs
        self.start()

    def run(self):
        if self.task == 'outliers':
            results = self.outliers(**self.kwargs)
            self.outlierEndSignal.emit(results)
        if self.task == 'detrend':
            results = self.fit(**self.kwargs)
            self.fitEndSignal.emit(results)

    def write(self, df, filename):
        df = df.dropna()
        # df = df.resample('D')
        header = '''# time_unit: %s
# unit: %s
# scale: 1
# column_names: %s
# columns_index: %s
# index_cols: %s
# index_formats: %s\n''' % (self.time_unit, self.unit,
                            ' '.join(['ymd', 'hms'] + list(df.columns)),
                            ' '.join(
                                list(map(str, range(0, len(df.columns) + 2)))),
                            ' '.join(['ymd', 'hms']), '%Y%m%d %H%M%S')
        # if os.path.isfile(filename):
        #     os.remove(filename)
        with open(filename, 'w') as f:
            f.write(header)
            df.to_csv(f, sep='\t', float_format='%10.4f',
                      index=True, header=False, date_format='%Y%m%d %H%M%S')
            # df.to_csv(f, sep='\t', float_format='%10.4f', na_rep='nan',
            #           index=True, header=False, date_format='%Y%m%d %H%M%S')

    def cumsum(self, df):
        df = df.cumsum() - df.mean()
        return df

    def diff(self, df):
        df = df.diff()
        return df
