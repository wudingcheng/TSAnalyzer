# encoding:utf-8
from ctypes import *
import numpy as np
from sys import platform

if "win" in platform:
    seglib = cdll.LoadLibrary("./TSModel/sigseg/libseg1d.dll")
else:
    seglib = cdll.LoadLibrary("./TSModel/sigseg/libseg1d.so")


class func_params(Structure):
    _fields_ = [('alpha', c_double),
                ('beta', c_double),
                ('epsilon', c_double),
                ('gamma', c_double),
                ('lambda_eps', c_double),
                ('mu_eps', c_double)]


class shp_fun_int(Structure):
    _fields_ = [('pp', POINTER(c_double)),
                ('ppd', POINTER(c_double)),
                ('f11', POINTER(c_double)),
                ('f12', POINTER(c_double)),
                ('f22', POINTER(c_double)),
                ('pf1', POINTER(c_double)),
                ('pf2', POINTER(c_double)),
                ('f11dd', POINTER(c_double)),
                ('f12dd', POINTER(c_double)),
                ('f22dd', POINTER(c_double)),
                ('ppf11d', POINTER(c_double)),
                ('ppf12d', POINTER(c_double)),
                ('ppf22d', POINTER(c_double)),
                ('ppf11dd', POINTER(c_double)),
                ('ppf12dd', POINTER(c_double)),
                ('ppf22dd', POINTER(c_double)), ]


class pos_idx_jhk(Structure):
    _fields_ = [('i', POINTER(c_int)),
                ('j', POINTER(c_int)),
                ('h', POINTER(c_int)),
                ('k', POINTER(c_int)), ]


class appx_u_sigma(Structure):
    _fields_ = [('u1', POINTER(c_double)),
                ('u2', POINTER(c_double)),
                ('s', POINTER(c_double)),
                ('sgm', POINTER(c_double))]


class combs(Structure):
    _fields_ = [('j', POINTER(c_int)),
                ('h', POINTER(c_int)),
                ('k', POINTER(c_int)), ]


def _structure2dict(structure):
    return dict((f, getattr(structure, f)) for f, _ in structure._fields_)


def _dict2structure(d, structure):
    for key, val in d.iteritems():
        setattr(structure, key, val)


class sigseg(object):

    def __init__(self):
        super(sigseg, self).__init__()
        self._params = func_params()
        self.pos = pos_idx_jhk()
        self.sfi = shp_fun_int()
        self.apx = appx_u_sigma()
        self._setup()

    def _setup(self):
        # shp_fun_int
        for f, _ in self.sfi._fields_:
            if 'ppf' in f:
                n = 17
            else:
                n = 5
            temp = np.zeros(n, np.double)
            setattr(self.sfi, f, (c_double * n)(*temp))

        # pos_idx_jhk
        for f, _ in self.pos._fields_:
            temp = np.zeros(17, np.int)
            setattr(self.pos, f, (c_int * 17)(*temp))

    @property
    def params(self):
        return _structure2dict(self._params)

    @params.setter
    def params(self, params):
        return _dict2structure(params, self._params)

    def main(self, params, data):
        self.params = params
        mx_iter = params.get('mx_iter')
        tol = params.get("tol")
        length = len(data)

        u1 = np.zeros(length)
        u1[0] = (data[0] + 0.5 * data[1]) / 1.5
        for i in range(1, length - 1):
            u1[i] = 0.5 * (data[i] + 0.5 * (data[i - 1] + data[i + 1]))
        u1[length - 1] = (data[length - 1] + 0.5 * data[length - 2]) / 1.5
        u2 = np.zeros(length)
        s = [0.5 for i in range(length)]
        sgm = [0.5 for i in range(length)]

        for i in ['u1', 'u2', 's', 'sgm']:
            setattr(self.apx, i, (c_double * length)(*eval(i)))

        step = 0
        mx_diff = c_double(0.0)

        g_in = (c_double * length)(*data)
        seglib.setup(byref(self.sfi), length - 1, byref(self.pos))
        seglib.minimize(g_in, length, self._params, byref(self.apx), byref(self.sfi), self.pos, byref(mx_diff))

        step += 1
        while (mx_diff > tol) and (step < mx_iter):
            mx_diff = c_double(0.0)
            step += 1
            seglib.minimize(g_in, length, self._params, byref(self.apx), byref(self.sfi), self.pos, byref(mx_diff))

        apx_array = np.zeros((length, 4))
        apx_array[:, 0] = np.fromiter(self.apx.u1, dtype=np.double, count=length)
        apx_array[:, 1] = np.fromiter(self.apx.u2, dtype=np.double, count=length)
        apx_array[:, 2] = np.fromiter(self.apx.s, dtype=np.double, count=length)
        apx_array[:, 3] = np.fromiter(self.apx.sgm, dtype=np.double, count=length)
        return apx_array
