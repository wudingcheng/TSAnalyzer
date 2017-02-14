import numpy as np
import matplotlib.pyplot as plt
import TSModel as T
from TSModel.lombscargle import LombScargle
from datetime import datetime
DPI = 600
cols = ['north', 'east', 'up']

reader = T.TSReader()
reader.read_file('Example/CAND.sio.noamf_frame.pos')


def plot_neu(df, name, show_error=False, offsets=None, fit=None):
    plt.figure()
    for i, col in enumerate(cols):
        plt.subplot(311 + i)
        if show_error:
            plt.errorbar(df.index, df[col], df['%s_sigma' % col],
                         label=col.title(), fmt='ko',
                         markersize=1, capsize=2, linewidth=0.5, elinewidth=0.5)
        else:
            plt.plot(df.index, df[col], 'ko', label=col.title(), linewidth=0.5, markersize=1)
        plt.ylabel('%s ($mm$)' % col.title(), fontsize=10, fontname='sans-serif')
        plt.grid()
    # plt.show()
    if offsets:
        for key, value in offsets.iteritems():
            date = datetime.strptime(key, '%Y%m%d')
            for i, col in enumerate(cols):
                plt.subplot(311 + i)
                plt.axvline(date, color='r')
    if fit is not None:
        for i, col in enumerate(cols):
            plt.subplot(311 + i)
            plt.plot(fit.index, fit[col], '-r')
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.0)

    plt.savefig(name, dpi=DPI, bbox_inches='tight', pad_inches=0)

# plot_neu(reader.df, 'cand_outlier.png', show_error=True)

outliers_prm = {'sigma': [10, 10, 30]}
ind = reader.outliers(**outliers_prm)['sigma']
reader.df.ix[ind] = np.nan
# plot_neu(reader.df, 'remove_sigma.png', show_error=False)

offsets = T.TSOffsets.get_offsets('cand', file='Example/offsets.json')
outliers_prm = {'polys': 1, 'periods': [0.5, 1],
                'offsets': offsets, 'iqr_factor': 3, 'iqr_window': 365}
reader.kwargs = outliers_prm
ind = reader.outliers(**outliers_prm)['iqr']
reader.df.ix[ind] = np.nan
# plot_neu(reader.df, 'remove_iqr.png', offsets=offsets)

# fit = reader.fit(**outliers_prm)
# plot_neu(reader.df, 'fit.png', offsets=offsets, fit=fit['fit'])
# plot_neu(fit['continuous'], 'continuous.png')
# plot_neu(fit['residual'], 'residual.png')

outliers_prm.update({'periods': None})
fit = reader.fit(**outliers_prm)
# plot_neu(fit['residual'], 'detrend.png')
df = fit['residual'].dropna()
t = df.ix[:, 0]
frequency = np.linspace(0.01, 20, len(t))
plt.figure()
for i, c in enumerate(cols):
    y = df[c].values
    dy = df['%s_sigma' % c].values
    p = LombScargle(t, y, dy).power(frequency)
    line = plt.loglog(frequency, p, label=c.title())
plt.legend(loc='best', fontsize=10, ncol=3)
# plt.grid()
plt.gca().xaxis.grid(which='both')
plt.gca().yaxis.grid(which='major')
plt.ylabel('Power', fontsize=10, fontname='sans-serif')
plt.xlabel('Frequency (cpy)', fontsize=10, fontname='sans-serif')
plt.savefig('spectrum.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
