#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import WLS
from itertools import compress
from ..models.offsets import OffsetEvent


class TSFit(object):

    def __init__(self, series):
        """
        series: index datetime, t, year in float, y, observation, dy if available
        """
        self.series = series.dropna()
        self.series.loc[:, 't'] = self.series['t'] - self.series['t'][0]
        if 'dy' not in self.series:
            self.series['dy'] = np.ones_like(self.series['t'])
        self.nepochs = len(self.series)

    def _aic(self, v, k):
        N = len(v)
        return 2 * k + N * np.log(sum(v**2) / N)

    def outliers(self, **kwargs):
        sigma = kwargs.get('sigma', 0)
        if sigma:
            inds = self.series['dy'] < sigma
            self.series = self.series[inds]
        iqr_factor = kwargs.get('iqr_factor', 0)
        if iqr_factor:
            iqr_window = kwargs['iqr_window']
            result = self.fit(**kwargs['lst'])
            residuals = pd.Series(result.resid, index=self.series.index)
            median = residuals.rolling(window=iqr_window).median().fillna(method='bfill')
            q75 = residuals.rolling(window=iqr_window).quantile(0.75).fillna(method='bfill')
            q25 = residuals.rolling(window=iqr_window).quantile(0.25).fillna(method='bfill')
            qrange = iqr_factor * (q75 - q25)
            low = median - qrange
            high = median + qrange
            inds = np.logical_and(residuals > low, residuals < high)
            self.series = self.series[inds]
        return self.series

    def fit(self, polys=1, periods=None, discontinuities=None):
        timespan = self.series['t'].max() - self.series['t'].min()
        date_start = self.series.index[0]
        date_end = self.series.index[-1]
        if periods:
            periods = np.array(periods)
            ind = periods * 3 < timespan
            periods = periods[ind]

        if discontinuities:
            discontinuities = sorted(discontinuities)
            discontinuities = [i for i in discontinuities if date_start < i.date < date_end]

        if polys == -1:
            polys = self.determineBestPolys(periods=periods,
                                            discontinuities=discontinuities)

        return self._fit(polys=polys, periods=periods, discontinuities=discontinuities)

    def determineBestPolys(self, periods=None, discontinuities=None):
        aics = [self._fit(polys=i, periods=periods, discontinuities=discontinuities)['aic'] for i in range(1, 11)]
        polys = aics.index(min(aics)) + 1
        return polys

    def getDesignMatrix(self, polys=1, periods=None, discontinuities=None):
        degrees = range(0, polys + 1)
        parameters = []
        t = self.series['t']
        self.nepochs = len(t)
        A = np.ones((polys + 1, self.nepochs))
        for degree in degrees:
            A[degree, :] = (t - t[0]) ** degree
            parameters.append('t**{}'.format(degree))

        if len(periods) > 0:
            dpi_t = 2.0 * np.pi * t
            for period in periods:
                B = np.zeros((2, self.nepochs))
                B[0, :] = np.sin(dpi_t / period)
                B[1, :] = np.cos(dpi_t / period)
                parameters += ['{} cycle sin'.format(period),
                               '{} cycle cos'.format(period)]
                A = np.vstack((A, B))

        for discontinuity in discontinuities:
            function, parameter = discontinuity.getFunctionAndParameters(t)
            A = np.vstack((A, function))
            parameters += parameter

        A = A.T
        return A, parameters

    def _fit(self,
             polys=1,
             periods=None,
             discontinuities=None):
        A, parameters = self.getDesignMatrix(polys=polys, periods=periods, discontinuities=discontinuities)
        # A = pd.DataFrame(A, columns=parameters)
        model = WLS(self.series['y'], A, weights=self.series['dy'])
        model.data.xnames = parameters
        result = model.fit()
        import pickle
        pickle.dump(A, open('A.pkl', 'wb'))
        pickle.dump(result, open('Result.pkl', 'wb'))
        return result
        P = np.diag(1.0 / self.series['dy'] ** 2)
        AP = np.dot(A.T, P)
        N = np.dot(AP, A)
        Q_xx = np.linalg.inv(N)
        W = np.dot(AP, self.series['y'])
        p = np.dot(Q_xx, W)
        pickle.dump(p, open('p.pkl', 'wb'))
        fit = np.dot(A, p)
        v = fit - self.series['y']
        result = {'parameters': parameters, 'p': p}
        result['v'] = v
        result['fit'] = fit
        result['aic'] = self._aic(v, A.shape[1])
        sigma2 = np.dot(np.dot(v.T, P), v) / (self.nepochs - A.shape[1])
        sigma_x = np.sqrt(np.diag(Q_xx * sigma2))
        result['psigma'] = sigma_x
        w = np.diag(P)
        chi_square = np.dot(v**2, w)
        result['chi_square'] = chi_square
        nrms = np.sqrt(chi_square / (self.nepochs - A.shape[1]))
        wrms = np.sqrt((self.nepochs / (self.nepochs - A.shape[1])) * chi_square / sum(w))
        result['nrms'] = nrms
        result['wrms'] = wrms
        return result

    def discontinuitiesSignificanceTest(self, discontinuities, polys=1, periods=None):
        # while 1:
        #     result = self._fit(polys=polys, periods=periods, discontinuities=discontinuities)
        #     j = polys + 1 + 2 * len(periods)
        #     psigma = result['psigma'][j:]
        #     p = result['p'][j:]
        #     temp = []
        #     for i, discontinuity in enumerate(discontinuities):
        #         npars = discontinuity.nParameters()
        #         p_ = p[:npars]
        #         psigma_ = psigma[:npars]
        #         p = p[npars:]
        #         psigma = psigma[npars:]
        #         if np.all(np.abs(p_) > 2 * psigma_):
        #             temp.append(discontinuity)
        #         # else:
        #
        #     if temp == discontinuities:
        #         print('test significance end', temp)
        #         return temp
        #
        #     discontinuities = temp
        # while 1:
        A, params = self.getDesignMatrix(polys=polys, periods=periods, discontinuities=discontinuities)
        model = WLS(self.series['y'], A, weights=self.series['dy'])
        model.data.xnames = params
        result = model.fit()
        # print(result.summary2())
        j = polys + 1 + 2 * len(periods)
        ind = result.pvalues[j:] < 0.05
        discontinuities = list(compress(discontinuities, ind))
        return discontinuities

    def _discontinutyFTest(self,
                           discontinuity,
                           polys=1,
                           periods=None,
                           discontinuities=None):
        A, _ = self.getDesignMatrix(polys=polys, periods=periods, discontinuities=discontinuities)
        _, chi_square, p1, _ = np.linalg.lstsq(A, self.series['y'])

        # discontinuities.remove(discontinuity)
        # A, _ = self.getDesignMatrix(polys=polys, periods=periods, discontinuities=discontinuities)
        ind = discontinuities.index(discontinuity) + polys + 2 * len(periods) + 1
        npar = discontinuity.nParameters()
        A = np.delete(A, range(ind, ind + npar), axis=1)
        _, chi_square_2, p2, _ = np.linalg.lstsq(A, self.series['y'])

        fvalue = (chi_square_2 - chi_square) * (self.nepochs - p1) / (chi_square * (p1 - p2))
        return fvalue[0]
        # return fvalue > F

    def discontinutyFTest(self, F=200, polys=1, periods=None, discontinuities=None):
        # from copy import dee
        while 1:
            # f = np.zeros(len(discontinuities))
            f = []
            flag = 0
            for i, discontinuity in enumerate(discontinuities):
                temp = discontinuities[:]
                fval = self._discontinutyFTest(discontinuity,
                                               polys=polys,
                                               periods=periods,
                                               discontinuities=temp)
                f.append(fval)
                # if fval < F:
                #     discontinuities.pop(i)
                #     break
                # else:
                #     flag += 1
            # if flag == len(discontinuities):
            #     return discontinuities

            f_min = min(f)
            if f_min > F:
                return discontinuities
            else:
                ind = f.index(f_min)
                discontinuities.pop(ind)
            if len(discontinuities) == 0:
                return discontinuities

    def log(self, results):
        parameters = results['parameters']
        p = results['p']
        psigma = results['psigma']
        log = "NRMS: {:.1f}, WRMS {:.1f}\n".format(results['nrms'], results['wrms'])
        for par, v, sigma in zip(parameters, p, psigma):
            log += "{}: {:.6f} +- {:.6f}\n".format(par, v, sigma)
        return log
