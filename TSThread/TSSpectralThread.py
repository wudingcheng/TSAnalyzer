from numpy import array, diag, exp, linspace, log, poly1d, polyfit, sqrt
from PyQt4.QtCore import QThread

from TSModel.lombscargle import LombScargle


# from scipy.signal import periodogram


class TSSpectralThread(QThread):

    def __init__(self, figure):
        super(TSSpectralThread, self).__init__()
        self.figure = figure

    def lombscargle(self, df, **kwargs):
        self.df = df
        # self.fit = kwargs['fi']
        self.kwargs = kwargs
        self._method = 'lombscargle'
        self.run()

    def _loglog_fit(self, freq, power):
        coeffs, covs = polyfit(
            log(freq), log(power), deg=1, cov=True)
        covs = sqrt(diag(covs))
        poly = poly1d(coeffs)
        yfit = lambda x: exp(poly(log(x)))
        yfit = yfit(freq)
        return yfit, coeffs[0], covs[0]

    def _lombscargle(self):
        cols = self.kwargs['cols']
        df = self.df.dropna()
        t = df.ix[:, 0]
        frequency = linspace(0.01, 20, len(t))
        for i, c in enumerate(cols):
            y = df[c].values
            dy = df['%s_sigma' % c].values
            p = LombScargle(t, y, dy).power(frequency)
            line = self.ax.plot(frequency, p, label=c, picker=3)
            if self.kwargs.get('fit', False):
                yfit, slope, sigma = self._loglog_fit(frequency, p)
                self.ax.plot(frequency, yfit, color=line[0].get_color(),
                             label='%s $%.2f \pm %.2f$' % (c, slope, sigma))
        # return power

    def periodogram(self, df, **kwargs):
        self.df = df
        self.kwargs = kwargs
        self._method = 'periodogram'
        self.run()

    def _periodogram(self):
        cols = self.kwargs['cols']
        df = self.df.dropna()
        window = self.kwargs.get('window', None)
        print window
        t = df.ix[:, 0]
        fs = 1.0 / (t[1] - t[0])
        for i, c in enumerate(cols):
            y = array(df[c].values)
            f, p = periodogram(y, fs, scaling='spectrum', window=window)
            self.ax.plot(f, p, label=c, picker=3)
            self.ax.hold(True)

    def run(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        # cols = self.kwargs['cols']
        # df = self.df.dropna()
        # t = df.ix[:, 0]
        # frequency = linspace(0.01, 20, len(t))
        # # result = {'frequency': frequency}
        # for i, c in enumerate(cols):
        #     y = df[c].values
        #     dy = df['%s_sigma' % c].values
        #     p = LombScargle(t, y, dy).power(frequency)
        #     ax.plot(frequency, p, label=c, picker=3)
        #     ax.hold(True)
        getattr(self, '_%s' % self._method)()
        self.figure.suptitle(self.kwargs.get('title', ''), fontsize='x-large')
        self.ax.set_xlabel('Frequceny')
        self.ax.set_ylabel('Power')
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=0.1, top=0.95)
        self.ax.legend()
        self.figure.canvas.draw_idle()
