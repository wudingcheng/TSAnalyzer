# encoding: utf-8
# author: WU Dingcheng

# from PyQt4.QtCore import pyqtSignal, pyqtSlot
# from PyQt4.QtGui import QDialog
from qtpy.QtCore import Signal, Slot
from qtpy.QtWidgets import QDialog

import numpy as np

from .SigsegDialog import Ui_Dialog as SigsegDialog
from .NavigationToolBar import NavigationToolbar
from .matplotlibwidget import MatplotlibWidget


class TSSigsegDialog(QDialog, SigsegDialog):
    addOffsetsSignal = Signal(dict)

    def __init__(self, parent=None):
        super(TSSigsegDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.matplotlibwidget = MatplotlibWidget()
        self.vlayout.addWidget(self.matplotlibwidget)
        self.figure = self.matplotlibwidget.figure
        self.figure.canvas.mpl_connect('pick_event', self.onpick)
        self.figure.subplots_adjust(left=0.1,
                                    right=0.90,
                                    top=0.95,
                                    bottom=0.05,
                                    wspace=0.0,
                                    hspace=0.05)
        self.figure.set_facecolor((1, 1, 1, 0))
        # self.figure.canvas.mpl_connect('motion_notify_event', self.hover)
        self.hover_marker = None
        self.toolbar = NavigationToolbar(self.figure.canvas, None, coordinates=False)
        self.toolbar.setStyleSheet("border:none")
        self.vlayout.insertWidget(0, self.toolbar)

        self.listWidget.doubleClicked.connect(self.on_listWidget_doubleClicked)
        self._line = None
        # ax = self.figure.add_subplot(111)
        # line, = ax.plot([1, 2, 3], '+', picker=5)
        # self.line = {'north': line}
        # self.figure.canvas.draw()
        # self.listWidget.addItems(["0", "1", "2"])

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, line):
        self._line = line
        self.line2list()

    def line2list(self):
        self.listWidget.clear()
        items = []
        for col, l in self._line.iteritems():
            xdata = l.get_xdata()
            for i in xdata:
                items.append('%s %s' % (col, str(i)))

        self.listWidget.addItems(items)

    @Slot()
    def on_addButton_clicked(self):
        offsets = {}
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            col, date = str(item.text()).split()
            date = date.replace('-', '')[:8]
            components = {col: 'ep'}
            if date not in offsets:
                offsets[date] = components
            else:
                offsets[date].update(components)
        self.addOffsetsSignal.emit(offsets)
        self.close()

    @Slot(name='on_deleteButton_clicked')
    def on_listWidget_doubleClicked(self):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if self.listWidget.isItemSelected(item):
                self.delete_point(str(item.text()))
                self.listWidget.takeItem(i)
        self.figure.canvas.draw()

    def delete_point(self, text):
        col, date = text.split()
        date = np.datetime64(date)
        x, y = self.line[col].get_data()
        newx = x[~np.in1d(x, date)]
        newy = y[~np.in1d(x, date)]
        self.line[col].set_data(newx, newy)

    def onpick(self, event):
        clicked_line = event.artist
        for col, line in self.line.iteritems():
            if clicked_line == line:
                ind = event.ind
                x, y = line.get_data()
                x = np.delete(x, ind)
                y = np.delete(y, ind)
                line.set_data(x, y)
                self.line2list()
                if self.hover_marker:
                    self.hover_marker = self.hover_marker.remove()
                self.figure.canvas.draw()
                break

                # def hover(self, event):
                #     for col, line in self.line.iteritems():
                #         if line.contains(event)[0]:
                #             res = line.contains(event)
                #             if res[0]:
                #                 if self.hover_marker is None:
                #                     x, y = line.get_data()
                #                     x = x[res[1]['ind']]
                #                     y = y[res[1]['ind']]
                #                     ax = event.inaxes
                #                     self.hover_marker = ax.scatter(x, y, s=100, alpha=0.3, c='r')
                #                 self.figure.canvas.draw()

                #         else:
                #             if self.hover_marker:
                #                 self.hover_marker = self.hover_marker.remove()
                #                 self.figure.canvas.draw()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    m = TSSigsegDialog()
    m.show()
    app.exec_()
