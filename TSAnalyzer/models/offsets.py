#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-
from __future__ import division
import json
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.dates as mdate
from ..algorithms.date import date2yearfraction

class DiscontinuityEvent(object):
    name = 'discontinuity'
    description = 'discontinuity event in GPS time series'
    color = 'k'

    def __init__(self, date, component, line=None):
        if isinstance(date, datetime):
            self.date = date
        else:
            self.date = pd.to_datetime(date)
        self.component = component
        self.line = line

    def getFunctionAndParameters(self, t):
        """
        :param t: pd.series, index datetime, value, float
        :return:
        """
        raise NotImplementedError

    def attachLine(self, line):
        """
        :param line: matplotlib line2D
        :return:
        """
        self.line = line

    def statusChanged(self):
        if self.line is not None:
            self.line.set_color(self.color)
            self.line.set_xdata(mdate.date2num(self.date))
            self.line.figure.canvas.draw_idle()

    def lineMoved(self):
        self.date = mdate.num2date(self.line.get_xdata()[0]).replace(tzinfo=None)
        self.line.figure.canvas.draw_idle()

    def dateStr(self, fmt="%Y%m%d"):
        return datetime.strftime(self.date, fmt)

    @classmethod
    def getColor(cls):
        return cls.color

    @classmethod
    def getIcon(cls):
        return cls.name

    @classmethod
    def getName(cls):
        return cls.name

    @classmethod
    def getDescription(cls):
        return cls.description

    @classmethod
    def nParameters(cls):
        raise  NotImplementedError

    def __repr__(self):
        return "{} {} {}".format(
            datetime.strftime(self.date, "%Y%m%d"),
            self.component,
            self.name)

    def __eq__(self, other):
        # flag = self.date == other.date and self.component == other.component
        # if not flag:
        #     return flag
        # tau = getattr(self, 'tau', None)
        # if tau:
        #     return flag and tau == other.tau
        # else:
        #     return flag
        return self.date == other.date and self.component == other.component

    def __lt__(self, other):
        return self.date < other.date

    def __hash__(self):
        return hash(self.__repr__())

    # def __del__(self):
    #     print('delete')
    #     if self.line:
    #         self.line.remove()


class OffsetEvent(DiscontinuityEvent):
    name = "offset"
    description = "Simple jump event"
    color = 'k'
    key = 'alt+1'

    def getFunctionAndParameters(self, t):
        A = np.zeros_like(t)
        ind = t.index > self.date
        A[ind] = 1
        return A, [self.__repr__()]

    @classmethod
    def nParameters(cls):
        return 1


class TrendChangeEvent(DiscontinuityEvent):
    name = 'trendchange'
    description = 'Trend change event'
    color = 'c'
    key = 'alt+2'

    def getFunctionAndParameters(self, t):
        A = np.zeros_like(t)
        ind = t.index > self.date
        A[ind] = t[ind] - t[ind][0]
        return A, [self.__repr__()]

    @classmethod
    def nParameters(cls):
        return 1


class LogDecayOffsetEvent(DiscontinuityEvent):
    name = 'logdecay'
    color = 'g'
    description = 'A log decay event'
    key = 'alt+3'

    def __init__(self, date, component, tau=1, line=None):
        super(LogDecayOffsetEvent, self).__init__(date, component, line=line)
        self.tau = int(tau)

    def getFunctionAndParameters(self, t):
        A = np.zeros((2, len(t)))
        ind = t.index > self.date
        A[0, ind] = 1
        A[1, ind] = np.log(1 + (t[ind] - t[ind][0]) * 365.25 / self.tau)
        return A, ["{} level shift".format(self.__repr__()),
                   "{} parameter".format(self.__repr__())]

    @classmethod
    def nParameters(cls):
        return 2

    def __repr__(self):
        return "{} {} {} tau {}".format(
            datetime.strftime(self.date, "%Y%m%d"),
            self.component,
            self.name,
            self.tau)


class ExpDecayOffsetEvent(DiscontinuityEvent):
    name = 'expdecay'
    color = 'b'
    description = 'A exponential decay'
    key = 'alt+4'

    def __init__(self, date, component, tau=1, line=None):
        super(ExpDecayOffsetEvent, self).__init__(date, component, line=line)
        self.tau = int(tau)

    def getFunctionAndParameters(self, t):
        A = np.zeros((2, len(t)))
        ind = t.index > self.date
        A[0, ind] = 1
        A[1, ind] = 1 - np.exp(-(t[ind] - t[ind][0]) * 365.25 / self.tau)
        return A, ["{} level shift".format(self.__repr__()),
                   "{} parameter".format(self.__repr__())]

    def __repr__(self):
        return "{} {} {} tau {}".format(
            datetime.strftime(self.date, "%Y%m%d"),
            self.component,
            self.name,
            self.tau)

    @classmethod
    def nParameters(cls):
        return 2


from collections import OrderedDict

DISCONTINUITIES = OrderedDict([("offset", OffsetEvent),
                              ("trendchange", TrendChangeEvent),
                              ("logdecay", LogDecayOffsetEvent),
                              ("expdecay", ExpDecayOffsetEvent)])


class TSOffsetsHandler(object):
    def __init__(self):
        self.offsets = {}

    def str2discontinuity(self, s):
        s = s.split()
        discontinuity = DISCONTINUITIES[s[2]]
        s.pop(2)
        if len(s) > 2:
            s.pop(2)
        return discontinuity(*s)

    def getSiteOffsets(self, site):
        return self.offsets.get(site, [])

    def getSiteComponentOffsets(self, site, component):
        discontinuities = self.getSiteOffsets(site)
        discontinuities = [i for i in discontinuities if i.component == component]
        return discontinuities

    def siteOffsetsToStrList(self, site):
        return [str(i) for i in self.getSiteOffsets(site)]

    def _toStrOffsets(self):
        saved = {}
        for site, offsets in self.offsets.items():
            saved[site] = self.siteOffsetsToStrList(site)
        return saved

    def saveToJSONFile(self, filename):
        offsets = self._toStrOffsets()
        with open(filename, 'w') as f:
            f.write(json.dumps(offsets, indent=4))

    def saveToTextFile(self, filename):
        offsets = self._toStrOffsets()
        lines = []
        for site, items in offsets.items():
            lines.append(["{} {}".format(site, i) for i in items])
        with open(filename, 'w') as f:
            f.write("\n".join(lines))

    def fromJSONFile(self, filename):
        with open(filename, 'r') as f:
            offsets = json.loads(f.read())

        for site, items in offsets.items():
            temp = self.offsets.get(site, [])
            temp.extend([self.str2discontinuity(i) for i in items])
            temp = list(set(temp))
            self.offsets[site] = temp

    def updateDiscontinuity(self, site, old, new):
        offsets = self.getSiteOffsets(site)
        if old in offsets:
            offsets.remove(old)
            offsets.append(new)

    def addDiscontinuity(self, site, discontinuity):
        offsets = self.getSiteOffsets(site)
        if discontinuity not in offsets:
            offsets.append(discontinuity)
            self.offsets[site] = offsets

    def addDiscontinuities(self, site, discontinuities):
        offsets = self.getSiteOffsets(site)
        offsets = list(set(offsets + discontinuities))
        self.offsets[site] = offsets

    def removeDiscontinuity(self, site, discontinuity):
        offsets = self.getSiteOffsets(site)
        if discontinuity in offsets:
            self.offsets[site].remove(discontinuity)
            if discontinuity.line:
                discontinuity.line.remove()
