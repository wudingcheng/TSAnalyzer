#!usr/env/bin python
# author: WU Dingcheng
import cvxpy as cvx
import numpy as np
from scipy.sparse import eye, csr_matrix, hstack, linalg
from scipy.signal import argrelextrema
from .fit import TSFit
from ..models.offsets import OffsetEvent, TrendChangeEvent


def gen_d2(n):
    """
    Generate the 2nd difference matrix.
    :param n: int, length of time series
    :return: csr_matrix, sparse matrix
    """
    I2 = eye(n - 2)
    O2 = csr_matrix((n - 2, 1))
    return hstack((I2, O2, O2)) + hstack((O2, -2 * I2, O2)) + hstack((O2, O2, I2))


def gen_d1(n):
    """
    Generate the 1st difference matrix
    :param n: int, length of time series
    :return: csr_matrix, sparse matrix
    """
    I1 = eye(n - 1)
    O1 = csr_matrix((n - 1, 1))
    return hstack((I1, O1)) - hstack((O1, I1))


def get_max_lam(y):
    """
    Calculate the max lambda value for given time series y
    :param y: np.array, time series given
    :return: float, max lambda value
    """
    D = gen_d2(len(y))
    ddt = D.dot(D.T)
    dy = D.dot(y)
    return np.linalg.norm(linalg.spsolve(ddt, dy), np.inf)


def get_max_rho(y):
    """
    Calculate the max rho value for given time series y,
    :param y: np.array, time series given
    :return: float, max rho value
    """
    D = gen_d1(len(y))
    ddt = D.dot(D.T)
    dy = D.dot(y)
    return np.linalg.norm(linalg.spsolve(ddt, dy), np.inf)


def l1filter(t, y,
             lam=1200,
             rho=80,
             periods=(365.25, 182.625),
             solver=cvx.MOSEK,
             verbose=False):
    """
    Do l1 regularize for given time series.
    :param t: np.array, time
    :param y: np.array, time series value
    :param lam: lambda value
    :param rho: rho value
    :param periods: list, periods, same unit as t
    :param solver: cvx.solver
    :param verbose: bool, show verbose or not
    :return: x, w, s, if periods is not None, else return x, w
    """
    t = np.asarray(t, dtype=np.float64)
    t = t - t[0]
    y = np.asarray(y, dtype=np.float64)

    assert y.shape == t.shape

    n = len(t)
    D = gen_d2(n)

    x = cvx.Variable(n)
    w = cvx.Variable(n)
    errs = y - x - w
    seasonal = None
    if periods:
        tpi_t = 2 * np.pi * t
        for period in periods:
            a = cvx.Variable()
            b = cvx.Variable()
            temp = a * np.sin(tpi_t / period) + b * np.cos(tpi_t / period)
            if seasonal is None:
                seasonal = temp
            else:
                seasonal += temp
        errs = errs - seasonal
    obj = cvx.Minimize(0.5 * cvx.sum_squares(errs) +
                       lam * cvx.norm(D * x, 1) +
                       rho * cvx.tv(w))
    prob = cvx.Problem(obj)
    prob.solve(solver=solver, verbose=verbose)
    if periods:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0], np.array(seasonal.value)[:, 0]
    else:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0], None
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(t)
    x = cvx.Variable(n)
    w = cvx.Variable(n)
    dx = cvx.mul_elemwise(1.0 / np.diff(t), cvx.diff(x))
    x_term = cvx.tv(dx)
    dw = cvx.mul_elemwise(1.0 / np.diff(t), cvx.diff(w))
    w_term = cvx.norm(dw, 1)
    errs = y - x - w
    seasonal = None
    if periods:
        tpi_t = 2 * np.pi * t
        for period in periods:
            a = cvx.Variable()
            b = cvx.Variable()
            temp = a * np.sin(tpi_t / period) + b * np.cos(tpi_t / period)
            if seasonal is None:
                seasonal = temp
            else:
                seasonal += temp
        errs = errs - seasonal

    obj = cvx.Minimize(0.5 * cvx.sum_squares(errs) + lam * x_term + rho * w_term)
    prob = cvx.Problem(obj)
    prob.solve(solver=solver, verbose=verbose)
    if periods:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0], np.array(seasonal.value)[:, 0]
    else:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0], None

def detrend(t, y):
    pass

def l1wrapper(series,
              name,
              solver=cvx.MOSEK,
              periods=(0.5, 1),
              polys=1,
              lam=1200,
              rho=80,
              threshold=200,
              offset=True,
              trendchange=True):
    if not (offset or trendchange):
        return []
    x, w, s = l1filter(series['t'], series['y'], periods=periods, lam=lam, rho=rho)

    discontinuities = []
    d2x = np.abs(np.diff(x, 2))
    d2x[d2x < 0.01] = 0
    # d2x[d2x < np.percentile(d2x, 95)] = 0.0
    ind = argrelextrema(d2x, np.greater, order=7)
    flag = ind[0] + 2
    trendchanges = series.index[flag]
    for t in trendchanges:
        temp = TrendChangeEvent(t, name)
        discontinuities.append(temp)

    dw = np.abs(np.diff(w))
    dw[dw < 0.1] = 0.0
    # dw[dw < np.percentile(dw, 95)] = 0.0
    ind = argrelextrema(dw, np.greater, order=7)
    flag = ind[0] + 1
    offsets = series.index[flag]
    for o in offsets:
        temp = OffsetEvent(o, name)
        discontinuities.append(temp)

    if len(discontinuities) == 0:
        return discontinuities


    tsfit = TSFit(series)
    discontinuities = tsfit.discontinuitiesSignificanceTest(discontinuities, polys=polys, periods=periods)
    # return discontinuities
    # trendchanges = [i for i in discontinuities if isinstance(i, TrendChangeEvent)]
    # offsets = [i for i in discontinuities if isinstance(i, OffsetEvent)]
    discontinuities = tsfit.discontinutyFTest(F=threshold,
                                               polys=polys,
                                               periods=periods,
                                               discontinuities=discontinuities)
    # for discontinuity in discontinuities:
    #     temp = deepcopy(discontinuities)
    #     flag = tsfit.discontinutyFTest(discontinuity,
    #                                    F=threshold,
    #                                    polys=polys,
    #                                    periods=periods,
    #                                    discontinuities=temp)
    #     if not flag:
    #         discontinuities.remove(discontinuity)

    # for discontinuity in discontinuities:
    #     temp = deepcopy(discontinuities)
    #     flag = tsfit.discontinutyFTest(discontinuity,
    #                                    F=threshold,
    #                                    polys=polys,
    #                                    periods=periods,
    #                                    discontinuities=temp)
    #     if not flag:
    #         discontinuities.remove(discontinuity)
    temp = []
    for discontinuity in discontinuities:
        if offset and isinstance(discontinuity, OffsetEvent):
            temp.append(discontinuity)
        if trendchange and isinstance(discontinuity, TrendChangeEvent):
            temp.append(discontinuity)
    return temp
