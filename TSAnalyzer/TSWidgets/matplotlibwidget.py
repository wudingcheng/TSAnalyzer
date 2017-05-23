from qtpy.QtWidgets import QSizePolicy
from qtpy.QtCore import QSize, PYQT_VERSION_STR, Qt
from matplotlib.figure import Figure
from matplotlib import rcParams

if float(PYQT_VERSION_STR[:3]) < 5:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
else:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas


rcParams['font.size'] = 12


class MatplotlibWidget(Canvas):

    def __init__(self, parent=None, width=4, height=3, dpi=100, hold=False):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        Canvas.__init__(self, self.figure)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setParent(parent)
        Canvas.setSizePolicy(self,
                             QSizePolicy.Expanding,
                             QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QMainWindow, QApplication
    from numpy import linspace

    class ApplicationWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self.mplwidget = MatplotlibWidget(self)
            self.mplwidget.setFocus()
            self.setCentralWidget(self.mplwidget)
            self.plot()

        def plot(self):
            axes = self.mplwidget.figure.add_subplot(111)
            x = linspace(-10, 10)
            axes.plot(x, x**2)
            axes.plot(x, x**3)

    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    sys.exit(app.exec_())
