# TSAnalyzer 2.0.1

## Requirements

- qtpy
- Matplotlib
- Numpy
- Pandas
- cvxpy
- cvxopt

## Installation

Before installing this package, the above requirements should be installed. For windows user, `cvxpy` package and its dependencies can be download at [[Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/)].

The [Anaconda](https://anaconda.org/) is recommended to be installed. *TSAnalyzer* can support both Python2 and Python3. *TSAnalyzer* is planning to pnly support Python3.

- Download this repo,  and `python setup.py install` on common line prompt.
- `pip install tsanalyzer`


After that, the package creates a command `tsanalyzer` in your path.

## Support and Information

For detail information and help, please refer to [DOC](doc/).

For more information and support, please contact me directly.

Email: wudingcheng14 at mails.ucas.ac.cn.

## Version Update

### v2.0.2 (2019/11/30)

- Support another neu format, traditionally  time of neu is calculated by `mjd = round(365.25 * (yearfraction - 1970.0) + 40587.0 + 0.1) - 0.5; date=date2mjd(mjd)`, this also support `(int(yearfraction), yearfraction - int(yearfraction)) * days_of_years)`, see `date.py` `yearfraction2mjd`, `fyear2date` for detail;
- add `continuous` time-series back from the v1.x, the `continuous` means no discontinuities in time series and outliers;
- Fix bug for read repeated station time-series;

### v2.0.1

- Fix bugs for *Header Convert Tool*;
- Fix bugs for `TSAnalyzer.models.reader`;
- Fix bugs for some UI layout;

## Todo

- Update L1 regularization for detection offsets and trendchanges;
- Offsets detection and output format;
- test scripts;

## License

GPL