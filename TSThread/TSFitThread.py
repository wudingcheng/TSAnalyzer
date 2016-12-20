from PyQt4.QtCore import QThread, pyqtSignal

from TSDate import date2yearfraction
from TSModel.TSFit import TSFit


class TSFitThread(QThread):

    detrendEndSignal = pyqtSignal(dict)

    def __init__(self, df, **kwargs):
        super(TSFitThread, self).__init__()
        self.df = df
        self.kwargs = kwargs

    def ts_fit(self):
        # index = self.df.index
        t = self.df[self.df.columns[0]]
        result = {}
        for i, c in enumerate(self.kwargs['cols']):
            tsfit = TSFit(t, self.df[c], cov=self.df['%s_sigma' % c])
            result[c] = tsfit.ts_fit(**self.kwargs)
        self.detrendEndSignal.emit(result)

    def ts_remove_outlier(self):
        t = self.df[self.df.columns[0]]
        for i, c in enumerate(self.kwargs['cols']):
            tsfit = TSFit(t, self.df[c], cov=self.df['%s_sigma' % c])
            result = tsfit.ts_fit(**self.kwargs)

    def run(self):
        self.ts_fit()
