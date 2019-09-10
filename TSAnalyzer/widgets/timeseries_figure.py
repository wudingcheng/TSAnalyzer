#!/usr/bin/env python
# -*- coding: utf-8 -*-
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction
from qtpy.QtCore import Signal, Qt, QThread, QCoreApplication
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.axes import Axes
from collections import OrderedDict
from .figure import MplCanvas
from ..models.offsets import DiscontinuityEvent, DISCONTINUITIES
from ..utils import makeAction
from ..thread.plot_thread import TimeSeriesThread

def _(text, disambiguation=None, context='TimeSeriesWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)



class TimeSeriesWidget(QWidget):
    sig_message_update = Signal(str)
    sig_discontinuity_added = Signal(datetime, Axes)
    sig_discontinuity_removed = Signal(DiscontinuityEvent)
    sig_discontinuity_moved = Signal(DiscontinuityEvent)
    sig_discontinuity_hovered = Signal(DiscontinuityEvent)
    sig_discontinuity_visibled = Signal()
    sig_files_plotted = Signal()

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(TimeSeriesWidget, self).__init__(parent=parent)
        self.mplCanvas = MplCanvas(parent=self, width=width, height=height, dpi=dpi)
        self.figure = self.mplCanvas.figure
        self.canvas = self.figure.canvas
        vb = QVBoxLayout(self)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)
        vb.addWidget(self.mplCanvas)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.cursor_enabled = False
        self._signals_connected = False

        self.thread = TimeSeriesThread(self.figure)
        self.thread.sig_time_series_end.connect(self.slotOnTimeSeriesPlotEnd)
        self.thread.finished.connect(self.canvas.draw_idle)

        self.discontinuityLines = {}
        self._discontinuityDragged = None

        self.componentsAxes = {}

        self.menu = QMenu()
        self.__initActions()

    def __initActions(self):
        _actions = [
            (self, _("Resize figure"), _("Resize Figure"), self.adjustFigure, 'figure.resize', None, False),
            None,
            (self, _("Grid lines"), _("Grid"), self.slotOnFigureGrid, 'figure.grid', None, True),
            (self, _("Show discontinuities"), _("Discontinuities"),
             self.slotOnVisibleDiscontinuities, 'figure.discontinuity', None, True)
        ]
        self.actions = OrderedDict()
        for act in _actions:
            if act is not None:
                a = makeAction(*act)
                self.actions[act[-3]] = a
                self.menu.addAction(a)
            else:
                self.menu.addSeparator()

        self.actions['figure.grid'].setChecked(True)
        self.actions['figure.discontinuity'].setChecked(True)

    def slotOnFigureGrid(self, flag):
        for ax in self.figure.axes:
            if flag:
                ax.grid(linestyle='--', color='k', alpha=0.2)
            else:
                ax.grid(flag)
        self.canvas.draw_idle()

    def slotOnVisibleDiscontinuities(self, flag):
        """For visible line from context menu action
        :param flag: bool 
        :return: 
        """
        for line in self.discontinuityLines.keys():
            line.set_visible(flag)
        if flag:
            self.sig_discontinuity_visibled.emit()
        self.canvas.draw_idle()

    def setDiscontinuitiesVisible(self, text):
        """For visible line from discontinuity dock
        :param text: DISCONTINUITY keys 
        :return: 
        """
        if text == "All":
            self.actions['figure.discontinuity'].setChecked(True)
            self.slotOnVisibleDiscontinuities(True)
            return
        obj = DISCONTINUITIES[text]
        for line, discontinuity in self.discontinuityLines.items():
            flag = isinstance(discontinuity, obj)
            line.set_visible(flag)
            self.actions['figure.discontinuity'].setChecked(False)
        self.canvas.draw_idle()

    def connectFigureEvent(self):
        self._mne_cid = self.canvas.mpl_connect('motion_notify_event', self.slotMouseMoved)
        self._bpe_cid = self.canvas.mpl_connect('button_press_event', self.slotMouseClickEvent)
        self._fee_cid = self.canvas.mpl_connect('figure_enter_event', self.slotEnterFigureEvent)
        self._fle_cid = self.canvas.mpl_connect('figure_leave_event', self.slotLeaveFigureEvent)
        self._aee_cid = self.canvas.mpl_connect('axes_enter_event', self.slotEnterAxesEvent)
        self._ale_cid = self.canvas.mpl_connect('axes_leave_event', self.slotLeaveAxesEvent)
        self._pke_cid = self.canvas.mpl_connect('pick_event', self.slotOnPickEvent)
        self._bre_cid = self.canvas.mpl_connect('button_release_event', self.slotOnButtonRelease)
        self._signals_connected = True

    def disconnectFigureEvent(self):
        for cid in (self._mne_cid, self._bpe_cid, self._fee_cid,
                    self._fle_cid, self._aee_cid, self._ale_cid,
                    self._pke_cid, self._bre_cid):
            cid = self.canvas.mpl_disconnect(cid)

    def __initAxes(self):
        # self.columns = ['north', 'east', 'up']
        for i, col in enumerate(self.columns):
            ax = self.axes[i]
            ax.grid(linestyle='--', color='k', alpha=0.2)
            ax.set_ylabel(col)

        self.adjustFigure()


    def adjustFigure(self):
        self.figure.subplots_adjust(top=0.95,
                                    bottom=0.1,
                                    left=0.1,
                                    right=0.95)
        self.canvas.draw_idle()

    def __initCursor(self):
        bbox = {
            'facecolor': 'k',
            'edgecolor': 'k',
            'alpha': 0.6,
            'pad': 0
        }
        styles = {'linewidth': 0.5, 'color': 'r'}
        self.verticalCursors = []
        self.horizontalCursors = []
        self.verticalLabels = []
        self.horizontalLabels = []
        self.annots = []
        for ax in self.axes:
            y1, y2 = ax.get_ylim()
            x1, x2 = ax.get_xlim()
            ymid = (y1 + y2) * 0.5
            xmid = (x1 + x2) * 0.5
            linev = ax.axvline(xmid, **styles)
            lineh = ax.axhline(ymid, **styles)
            self.verticalCursors.append(linev)
            self.horizontalCursors.append(lineh)
            label = ax.format_ydata(ymid).strip()
            labelh = ax.text(1, 0.5, label,
                             fontsize=10,
                             transform=ax.transAxes,
                             horizontalalignment='left',
                             color='w',
                             verticalalignment='center', bbox=bbox)
            label = ax.format_ydata(xmid).strip()
            labelv = ax.text(0.5, 0, label,
                             fontsize=10,
                             transform=ax.transAxes,
                             horizontalalignment='center',
                             color='w',
                             verticalalignment='top', bbox=bbox)
            self.horizontalLabels.append(labelh)
            self.verticalLabels.append(labelv)

            annot = ax.annotate("Hello World",
                                xy=(1, 1),
                                xytext=(1, 1),
                                transform=ax.transAxes,
                                horizontalalignment='center',
                                textcoords="offset points",
                                backgroundcolor=(1, 1, 1, 0.9))
            self.annots.append(annot)

        self.setLabelAndCursorVisible(False)

    def slotOnDataLoaded(self, reader):
        # if reader.columns != self.columns:
        self.discontinuityLines = {}
        if self._signals_connected:
            self.disconnectFigureEvent()
        self.columns = reader.columns
        self.thread.render(reader, task='ts')
        self.thread.start()

    def slotOnTimeSeriesPlotEnd(self):
        self.axes = self.figure.axes
        self.__initAxes()
        self.__initCursor()
        self.componentsAxes = {}
        for ax in self.axes:
            self.componentsAxes[ax.get_ylabel()] = ax
        self.connectFigureEvent()
        self.sig_files_plotted.emit()

    def slotOnFitOrResiduals(self, df, columns, task):
        self.discontinuityLines = {}
        self.thread.renderFitOrResiduals(df, columns, task)
        self.thread.start()

    def slotMouseMoved(self, evt):
        x, y = evt.x, evt.y
        label = ""

        self._ys = [0, 0, 0]
        for i, ax in enumerate(self.axes):
            inv = ax.transData.inverted()
            xdata, _y = inv.transform((x, y))
            label += "{}={:.1f} ".format(ax.get_ylabel(), _y)
            self._ys[i] = _y
        xdata = self.axes[-1].format_xdata(xdata).strip()
        label = "date={} {}".format(xdata, label)
        self.sig_message_update.emit(label)

        if evt.inaxes and self.cursor_enabled:
            self.slotCursorMoved(evt)

        if self._discontinuityDragged:
            self.slotOffsetMoved(evt)

    def _setAxesCursorVisible(self, ax):
        for cursor in self.horizontalCursors + self.verticalCursors:
            cursor.set_visible(ax == cursor.axes)
        for label in self.horizontalLabels + self.verticalLabels:
            label.set_visible(ax == label.axes)
        for annot in self.annots:
            annot.set_visible(ax == annot.axes)

    def slotCursorMoved(self, evt):
        self._setAxesCursorVisible(evt.inaxes)

        x1, x2 = evt.inaxes.get_xlim()
        y1, y2 = evt.inaxes.get_ylim()

        inv = evt.inaxes.transData.inverted()
        x, y = evt.x, evt.y
        xdata, ydata = inv.transform((x, y))
        xdata = evt.inaxes.format_xdata(xdata)

        for label in self.verticalLabels:
            label.set_x((evt.xdata - x1) / (x2 - x1))
            label.set_text(xdata)
        for label in self.horizontalLabels:
            label.set_y((evt.ydata - y1) / (y2 - y1))
            label.set_text("{:.2f}".format(ydata))
        for cursor in self.verticalCursors:
            cursor.set_xdata((evt.xdata, evt.xdata))
        for cursor in self.horizontalCursors:
            cursor.set_ydata((evt.ydata, evt.ydata))

        for line in self.discontinuityLines.keys():
            if line.contains(evt)[0]:
                line.set_linewidth(2)
                self.updateOffsetAnnotation(line)
                self.sig_discontinuity_hovered.emit(self.discontinuityLines[line])
                break
            else:
                line.set_linewidth(1)
        else:
            for annot in self.annots:
                annot.set_visible(False)


        self.canvas.draw_idle()

    def updateOffsetAnnotation(self, line):
        ax = line.axes
        annots = [i for i in self.annots if ax == i.axes]
        if len(annots) == 0:
            return
        annot = annots[0]
        annot.set_visible(True)
        pos = line.get_xydata()[1, :]
        annot.xy = (pos[0], ax.get_ylim()[1])
        if self._discontinuityDragged:
            text = mdates.num2date(pos[0]).strftime('%Y%m%d')
        else:
            text = str(self.discontinuityLines[line])
        annot.set_text(text)
        annot.set_color(line.get_color())

    def setCursorsColor(self, color):
        for cursor in self.horizontalCursors + self.verticalCursors:
            cursor.set_color(color)

    def slotMouseClickEvent(self, evt):
        print('mouseClickEvent', evt)
        # self.mouseClickEvent.emit(evt)

    def slotEnterFigureEvent(self, evt):
        # self.setLabelAndCursorVisible(True)
        pass

    def slotLeaveFigureEvent(self, evt):
        for line in self.discontinuityLines.keys():
            line.set_linewidth(1)
        for annot in self.annots:
            annot.set_visible(False)
        self.setLabelAndCursorVisible(False)

    def slotEnterAxesEvent(self, evt):
        # self.enterAxesEvent.emit(evt)
        # self.setLabelAndCursorVisible(True)
        pass

    def slotLeaveAxesEvent(self, evt):
        self.setLabelAndCursorVisible(False)

    def setLabelAndCursorVisible(self, flag):
        for item in self.horizontalLabels + self.horizontalCursors + \
                self.verticalLabels + self.verticalCursors:
            item.set_visible(flag)
        self.canvas.draw_idle()

    def slotMouseClickEvent(self, event):
        if event.inaxes and self.cursor_enabled and event.button == 1:
            date = mdates.num2date(event.xdata).replace(tzinfo=None)
            self.sig_discontinuity_added.emit(date, event.inaxes)

    def slotOnPickEvent(self, event):
        line = event.artist
        if line in self.discontinuityLines.keys():
            self.slotOnDiscontinuityPick(event)

    def slotOnDiscontinuityPick(self, event):
        line = event.artist
        if event.mouseevent.button == 3:
            discontinuity = self.discontinuityLines.pop(line)
            self.sig_discontinuity_removed.emit(discontinuity)
        elif event.mouseevent.button == 2:
            self._discontinuityDragged = self.discontinuityLines[line]

    def slotOnButtonRelease(self, evt):
        if evt.button == 2 and self._discontinuityDragged:
            self.sig_discontinuity_moved.emit(self._discontinuityDragged)
            self._discontinuityDragged = None

    def slotOffsetMoved(self, evt):
        if evt.xdata is not None:
            self._discontinuityDragged.line.set_xdata((evt.xdata, evt.xdata))

    def contextMenuEvent(self, event):
        if self.figure.axes and not self.cursor_enabled:
            self.menu.exec_(self.mapToGlobal(event.pos()))

