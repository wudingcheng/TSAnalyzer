# -*- coding: utf-8 -*-
#!/usr/bin/env python
# author: WU Dingcheng

from qtpy.QtCore import QObject, Signal
import pandas as pd
import os
from ..algorithms.date import (
    date2yearfraction,
    yearfraction2date,
    mjd2date,
    mjd2yearfraction,
    fyear2date,
)


class Reader(QObject):
    sig_file_read = Signal()
    sig_file_clear = Signal()

    def __init__(self, parent=None):
        super(Reader, self).__init__(parent=parent)
        self.df = None
        self.name = None
        self.skiprows = 0
        self.cols = None
        self.columns = None
        self.is_read = False

    def _readHeader(self, filename):
        if not os.path.isfile(filename):
            return
        name = None
        col_names = None
        col_indexs = None
        index = None
        formats = None
        support_time_units = ["years", "days"]
        time_unit = "years"
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("#"):
                    break
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
        filter_columns = [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "seconds",
            "doy",
            "ymd",
            "hms",
            "mjd",
        ]
        self.columns = [
            i for i in col_names if i not in filter_columns and "sigma" not in i
        ]
        self.columns = [i for i in self.columns if i not in support_time_units]
        if name is None:
            self.name = os.path.split(self.filename)[1][:4].upper()
        else:
            self.name = name
        self.cols = dict(zip(col_indexs, col_names))
        if index == ["mjd"]:
            self._readMJD()
            return
        self._parser_dates = {"datetime": index}
        # self._date_parser = lambda x: pd.datetime.strptime(x, formats)
        self._date_parser = formats

    def _readMJD(self):
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            self.filename,
            header=None,
            sep="\s+",
            comment="#",
            names=names,
            usecols=cols,
            skiprows=self.skiprows,
        )
        index = list(map(mjd2date, self.df["mjd"]))
        if self.time_unit == "years":
            years = list(map(mjd2yearfraction, self.df["mjd"]))
            self.df[self.time_unit] = years
        if self.time_unit == "days":
            self.df[self.time_unit] = self.df["mjd"]
        del self.df["mjd"]
        self.df.index = index
        self.df.index.name = "datetime"

    def readFile(self, filename):
        self.filename = filename
        self.df = None
        formats = os.path.splitext(filename)[1][1:]
        read_func = getattr(self, "_read{}".format(formats.upper()))
        read_func(filename)
        self.sig_file_read.emit()
        self.is_read = True

    def _readFile(self, filename):
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            filename,
            header=None,
            sep="\s+",
            comment="#",
            names=names,
            usecols=cols,
            index_col="datetime",
            parse_dates=self._parser_dates,
            # date_parser=self._date_parser,
            date_format=self._date_parser,
            skiprows=self.skiprows,
        )

    def _readPOS(self, filename):
        self.unit = "mm"
        self.scale = 1000
        self.time_unit = "years"
        with open(filename, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "ID" in line:
                    self.name = line.split(":")[1].strip()
                if line.startswith("*YYYYMMDD"):
                    self.skiprows = i + 1
                    break
                if line.startswith(" "):
                    self.skiprows = i
                    break
        self.columns = ["north", "east", "up"]
        self.cols = {
            0: "ymd",
            1: "hms",
            15: "north",
            16: "east",
            17: "up",
            18: "north_sigma",
            19: "east_sigma",
            20: "up_sigma",
        }
        # self._date_parser = lambda x: pd.datetime.strptime(x, "%Y%m%d %H%M%S")
        self._date_parser = "%Y%m%d %H%M%S"
        self._parser_dates = {"datetime": ["ymd", "hms"]}
        self._readFile(filename)
        self.df = self.df.apply(lambda i: i * self.scale)
        dys = date2yearfraction(list(self.df.index))
        self.df.insert(0, self.time_unit, dys)

    def _readDAT(self, filename):
        self._readHeader(filename)
        # if self.is_read:
        #     return
        self._readFile(filename)
        self.df = self.df.apply(lambda i: i * self.scale)
        if self.time_unit not in self.df.columns:
            if self.time_unit == "years":
                dys = date2yearfraction(list(self.df.index))
            if self.time_unit == "days":
                dys = self.df.index.to_julian_date()
            self.df = self.df[self.df.columns].apply(pd.to_numeric)
            self.df.insert(0, self.time_unit, dys)
        for col in self.columns:
            if "{}_sigma".format(col) not in self.df.columns:
                self.df["{}_sigma".format(col)] = 1

    def _readNEU(self, filename):
        self.name = os.path.split(self.filename)[1][:4].upper()
        self.unit = "mm"
        self.scale = 1000
        self.time_unit = "years"
        self.columns = ["north", "east", "up"]
        self.cols = {
            0: "years",
            1: "north",
            2: "east",
            3: "up",
            4: "north_sigma",
            5: "east_sigma",
            6: "up_sigma",
        }
        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            self.filename,
            header=None,
            sep="\s+",
            comment="#",
            names=names,
            usecols=cols,
        )
        self.df[self.df.columns[1:]] *= self.scale
        time_index = [yearfraction2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            time_index = [fyear2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            raise ValueError("NEU timestamp not support!")
        self.df.index = time_index
        self.df.index.name = "datetime"

    def _readTSERIES(self, filename):
        self.name = os.path.split(filename)[1][:4].upper()
        self.unit = "mm"
        self.scale = 1000
        self.time_unit = "years"
        self.columns = ["north", "east", "up"]
        self.cols = {
            0: "years",
            1: "east",
            2: "north",
            3: "up",
            4: "east_sigma",
            5: "north_sigma",
            6: "up_sigma",
            11: "year",
            12: "month",
            13: "day",
            14: "hour",
            15: "minute",
            16: "seconds",
        }
        # self._parser_dates = [11, 12, 13, 14, ...] # which is not right
        self._parser_dates = {
            "datetime": ["year", "month", "day", "hour", "minute", "seconds"]
        }
        # self._date_parser = lambda x: pd.datetime.strptime(x, "%Y %m %d %H %M %S")
        self._date_parser = "%Y %m %d %H %M %S"
        self._readFile(filename)
        self.df.iloc[:, 1:] = self.df.iloc[:, 1:].apply(lambda i: i * self.scale)

    def _readTENV(self, filename):
        self.name = os.path.split(filename)[1][:4].upper()
        self.unit = "mm"
        self.scale = 1000
        self.time_unit = "years"
        self.columns = ["north", "east", "up"]
        self.cols = {
            2: "years",
            6: "east",
            7: "north",
            8: "up",
            10: "east_sigma",
            11: "north_sigma",
            12: "up_sigma",
        }

        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            self.filename,
            header=None,
            sep="\s+",
            comment="#",
            names=names,
            usecols=cols,
        )
        self.df[self.df.columns[1:]] *= self.scale
        time_index = [yearfraction2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            time_index = [fyear2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            raise ValueError("NEU timestamp not support!")
        self.df.index = time_index
        self.df.index.name = "datetime"

    def _readTENV3(self, filename):
        self.name = os.path.split(filename)[1][:4].upper()
        self.unit = "mm"
        self.scale = 1000
        self.time_unit = "years"
        self.columns = ["north", "east", "up"]
        self.cols = {
            2: "years",
            8: "east",
            10: "north",
            12: "up",
            14: "east_sigma",
            15: "north_sigma",
            16: "up_sigma",
        }

        cols = sorted(self.cols.keys())
        names = [self.cols[i] for i in cols]
        self.df = pd.read_csv(
            self.filename,
            skiprows=1,
            header=None,
            sep="\s+",
            comment="#",
            names=names,
            usecols=cols,
        )
        self.df[self.df.columns[1:]] *= self.scale
        time_index = [yearfraction2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            time_index = [fyear2date(i) for i in self.df.years]
        if not (len(time_index) == len(set(time_index))):
            raise ValueError("NEU timestamp not support!")
        self.df.index = time_index
        self.df.index.name = "datetime"

    def saveTODAT(self, df, filename):
        df = df.dropna()
        header = (
            "# time_unit: {}\n"
            "# unit: {}\n"
            "# scale: 1\n"
            "# column_names: {}\n"
            "# columns_index: {}\n"
            "# index_cols: {}\n"
            "# index_formats: %Y%m%d %H%M%S\n"
        ).format(
            self.time_unit,
            self.unit,
            " ".join(["ymd", "hms"] + list(df.columns)),
            " ".join(list(map(str, range(0, len(df.columns) + 2)))),
            " ".join(["ymd", "hms"]),
        )

        with open(filename, "w") as f:
            f.write(header)
            df.to_csv(
                f,
                sep="\t",
                float_format="%10.4f",
                index=True,
                header=False,
                date_format="%Y%m%d %H%M%S",
            )

    def clear(self):
        self.is_read = False
        self.df = None
        self.name = None
        self.filename = None
        self.columns = None
        self.sig_file_clear.emit()
