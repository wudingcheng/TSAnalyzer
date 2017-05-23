# from PyQt4.QtCore import QThread, pyqtSignal
from qtpy.QtCore import QThread
from ..TSModel.sigseg import sigseg
import matplotlib.pyplot as plt


class TSOffsetsThread(QThread):

    def __init__(self):
        super(TSOffsetsThread, self).__init__()

    def render(self, data, prm):
        self.data = data - data.mean()

        self.prm = prm
        self.sig = sigseg()
        self.start()

    def run(self):
        data = self.sig.main(self.prm, self.data)
        plt.plot(data[:, 3])
        plt.show()
