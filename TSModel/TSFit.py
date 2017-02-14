from __future__ import division

import numpy as np


class TSFit(object):

    def __init__(self, t, y, cov=None):
        self.t = np.array(t, order='C')
        self.y = np.array(y, order='C')
        if not self.t.shape == self.y.shape:
            raise ValueError("t and y are not equal length")
        if np.ndim(self.t) != 1 or np.ndim(self.y) != 1:
            raise ValueError("t or y should be 1d array")
        self.cov = np.ones(self.t.shape)
        if cov is not None:
            self.cov = 1.0 / cov**2

    def _aic(self, v, k):
        N = len(v)
        return 2 * k + N * np.log(sum(v**2) / N)

    def ts_fit(self, **kwargs):
        ind = np.isnan(self.y)
        t = self.t[~ind]
        kwargs_copy = kwargs.copy()
        timespan = t[-1] - t[0]
        periods = kwargs.get('periods', None)
        offsets = kwargs.get('offsets', None)
        psdecays = kwargs.get('psdecays', None)
        if periods is not None:
            periods = np.array(periods)
            ind = periods * 3 < timespan
            kwargs_copy['periods'] = periods[ind]
        if offsets is not None and len(offsets) > 0:
            offsets = np.array(offsets)
            ind = np.logical_and(offsets > t[0], offsets < t[-1])
            kwargs_copy['offsets'] = offsets[ind]
        if psdecays is not None and len(psdecays) > 0:
            temp = []
            for psdecay in psdecays:
                if psdecay[0] > t[0] and psdecay[0] < t[-1]:
                    temp.append(psdecay)
            kwargs_copy['psdecays'] = temp
        poly_degree = kwargs.get('polys', 1)
        if poly_degree == 0:
            aics = []
            temp = kwargs_copy.copy()
            temp['full'] = False
            solves = []
            for i in range(1, 11):
                print i
                temp['polys'] = i
                solve = self._ts_fit(**temp)
                aics.append(solve['aic'])
                solves.append(solve)
                # todo here
                # if abs(solve['p'][-2 * len(periods) - 1]) < 0.01:
                #     break
            print aics
            ind = aics.index(min(aics))
            kwargs_copy['polys'] = ind + 1
            self.ts_kwargs = kwargs_copy
            # return solves[ind]
        else:
            kwargs_copy['polys'] = poly_degree
            self.ts_kwargs = kwargs_copy
        return self._ts_fit(**kwargs_copy)

    def _ts_fit(self, **kwargs):
        ind = np.isnan(self.y)
        t = self.t[~ind]
        y = self.y[~ind]
        cov = np.diag(self.cov[~ind])
        nepochs = len(t)
        periods = kwargs.get('periods', None)
        offsets = kwargs.get('offsets', None)
        psdecays = kwargs.get('psdecays', None)
        poly_degree = kwargs.get('polys', 1)
        degrees = range(0, poly_degree + 1)
        A = np.ones((poly_degree + 1, nepochs), order='C')
        for degree in degrees:
            A[degree, :] = (t - t[0]) ** degree

        if periods is not None:
            for period in periods:
                B = np.zeros((2, nepochs))
                B[0, :] = np.sin(2.0 * np.pi * t / period)
                B[1, :] = np.cos(2.0 * np.pi * t / period)
                A = np.vstack((A, B))

        if offsets is not None and len(offsets) > 0:
            for offset in offsets:
                B = np.zeros((1, nepochs))
                index = t > offset
                B[:, index] = 1
                A = np.vstack((A, B))
        # psdecay = [epoch, tau, type]
        # type:
        #       0, exponential
        #       1, logarithmic
        if psdecays is not None and len(psdecays) > 0:
            for psdecay in psdecays:
                B = np.zeros((2, nepochs))
                index = t > psdecay[0]
                B[0, :][index] = 1
                tau = psdecay[1] - psdecay[0]
                if psdecay[2] == 0:
                    # index = np.logical_and(t > psdecay[0], t < psdecay[1])
                    B[1, :][index] = 1 - np.exp(-(t[index] - psdecay[0]) / tau)
                elif psdecay[2] == 1:
                    B[1, :][index] = np.log(1 + ((t[index] - psdecay[0]) / tau))
                # elif psdecay[2] == 2:
                #     index = np.logical_and(t > psdecay[0], t < psdecay[1])
                #     B[1, :][index] = 1.0 / t[index]
                #     C = np.zeros((1, nepochs))
                #     C[:, index] = t[index]
                #     B = np.vstack((B, C))
                A = np.vstack((A, B))

        A = A.T
        P = cov
        AP = np.dot(A.T, P)
        N = np.dot(AP, A)
        Q_xx = np.linalg.inv(N)
        W = np.dot(AP, y)
        p = np.dot(Q_xx, W)
        fit = np.dot(A, p)
        v = fit - y
        result = kwargs
        result['p'] = p
        result['v'] = v
        number = len(kwargs.get('offsets', [])) + 2 * len(kwargs.get('psdecays', []))
        if number != 0:
            temp_p = np.copy(p)
            temp_p[:-number] = 0
            continuous = y - np.dot(A, temp_p)
            result['continuous'] = continuous
        else:
            result['continuous'] = y
        result['fit'] = fit
        result['aic'] = self._aic(v, A.shape[1])
        sigma2 = np.dot(np.dot(v.T, P), v) / (nepochs - A.shape[1])
        sigma_x = np.sqrt(np.diag(Q_xx * sigma2))
        result['sigma_x'] = sigma_x
        if kwargs.get('full', False):
            # Q = np.diag(1.0 / sigma**2)
            # Q = 1.0 / np.diag(cov)
            w = np.diag(cov)
            chi_square = np.dot(v**2, w)
            nrms = np.sqrt(chi_square / (nepochs - A.shape[1]))
            wrms = np.sqrt((nepochs / (nepochs - A.shape[1])) * chi_square / sum(w))
            result['nrms'] = nrms
            result['wrms'] = wrms
        return result
