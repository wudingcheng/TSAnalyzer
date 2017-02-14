from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QAction, QIcon

from NavigationToolBar import NavigationToolbar


class TSToolBar(NavigationToolbar):

    RangeDrawEndSignal = pyqtSignal(Rectangle)
    BreakLineDrawEndSignal = pyqtSignal(Line2D)

    def __init__(self, canvas, parent, coordinates=True):
        # self.interaction = TSInteraction(canvas.figure)
        # range selector
        self.rect = None
        self.rects = []
        self.pressv = None
        self.prev = None
        self.press_flag = False
        self.facecolor = 'b'
        self.alpha = 0.8
        super(TSToolBar, self).__init__(canvas, parent, coordinates=True)

    def _init_toolbar(self):
        super(TSToolBar, self)._init_toolbar()
        self.epBreakAction = QAction(
            QIcon(":/TSResource/images/ep-break.png"), "Equipment break", self)
        self.eqBreakAction = QAction(
            QIcon(":/TSResource/images/eq-break.png"), "Earthquake break", self)
        self.eqExpBreakAction = QAction(QIcon(":/TSResource/images/eq-exp.png"),
                                        "Earthquake exponential break", self)
        self.eqLogBreakAction = QAction(QIcon(":/TSResource/images/eq-log.png"),
                                        "Equipment logarithic break", self)
        self.errorbarAction = QAction(QIcon(":/TSResource/images/errorbar.png"), "Errorbar", self)
        # self.errorbarAction.setCheckable(True)
        # self.tsToolBar.addAction(self.errorbarAction)
        self.actions = [None, self.epBreakAction, self.eqBreakAction,
                        self.eqExpBreakAction, self.eqLogBreakAction,
                        None, self.errorbarAction]
        # self.tsToolBar.addSeparator()
        for action in self.actions:
            if action is None:
                self.addSeparator()
            else:
                self.addAction(action)
                action.setCheckable(True)
        self.errorbarAction.triggered.connect(self._click_errorbarAction)
        self.epBreakAction.triggered.connect(self._click_epBreakAction)
        self.eqBreakAction.triggered.connect(self._click_eqBreakAction)
        self.eqExpBreakAction.triggered.connect(self._click_eqExpBreakAction)
        self.eqLogBreakAction.triggered.connect(self._click_eqLogBreakAction)

    def _update_buttons_checked(self):
        super(TSToolBar, self)._update_buttons_checked()
        self.epBreakAction.setChecked(self._active == 'EPBREAK')
        self.eqBreakAction.setChecked(self._active == 'EQBREAK')
        self.eqExpBreakAction.setChecked(self._active == 'EQEXPBREAK')
        self.eqLogBreakAction.setChecked(self._active == 'EQLOGBREAK')

    def disconnect_events(self):
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

    def _click_epBreakAction(self, flag):
        if len(self.canvas.figure.get_axes()) != 0:
            self._active = None if self._active == 'EPBREAK' else 'EPBREAK'

            if self._idPress:
                self._idPress = self.canvas.mpl_disconnect(self._idPress)
                self._idDrag = self.canvas.mpl_disconnect(self._idDrag)

            if self._active:
                self._idPress = self.canvas.mpl_connect('button_press_event', self.break_press)
                self._idDrag = self.canvas.mpl_connect('motion_notify_event', self.cursor_motion)
                self.color = 'b'
                self.mode = 'epbreak'
                self.canvas.widgetlock(self)
            else:
                self.canvas.widgetlock.release(self)
        self._update_buttons_checked()

    def _click_eqBreakAction(self, flag):
        if len(self.canvas.figure.get_axes()) != 0:
            self._active = None if self._active == 'EQBREAK' else 'EQBREAK'

            if self._idPress:
                self._idPress = self.canvas.mpl_disconnect(self._idPress)
                self._idDrag = self.canvas.mpl_disconnect(self._idDrag)

            if self._active:
                self._idPress = self.canvas.mpl_connect('button_press_event', self.break_press)
                self._idDrag = self.canvas.mpl_connect('motion_notify_event', self.cursor_motion)
                self.color = 'r'
                self.mode = 'eqbreak'
                self.canvas.widgetlock(self)
            else:
                self.canvas.widgetlock.release(self)
        self._update_buttons_checked()

    def _click_eqExpBreakAction(self, flag):
        if len(self.canvas.figure.get_axes()) != 0:
            self._active = None if self._active == 'EQEXPBREAK' else 'EQEXPBREAK'

            if self._idPress:
                self._idPress = self.canvas.mpl_disconnect(self._idPress)
            if self._idDrag:
                self._idDrag = self.canvas.mpl_disconnect(self._idDrag)
            if self._idRelease:
                self._idRelease = self.canvas.mpl_disconnect(self._idRelease)

            if self._active:
                self._idPress = self.canvas.mpl_connect('button_press_event', self.range_on_press)
                self._idDrag = self.canvas.mpl_connect('motion_notify_event', self.range_on_move)
                self._idRelease = self.canvas.mpl_connect('button_release_event', self.range_on_release)
                self.mode = 'eqexpbreak'
                self.color = 'b'
                self.canvas.widgetlock(self)
            else:
                self.canvas.widgetlock.release(self)
        self._update_buttons_checked()

    def _click_eqLogBreakAction(self, flag):
        if len(self.canvas.figure.get_axes()) != 0:
            self._active = None if self._active == 'EQLOGBREAK' else 'EQLOGBREAK'

            if self._idPress:
                self._idPress = self.canvas.mpl_disconnect(self._idPress)
            if self._idDrag:
                self._idDrag = self.canvas.mpl_disconnect(self._idDrag)
            if self._idRelease:
                self._idRelease = self.canvas.mpl_disconnect(self._idRelease)

            if self._active:
                self._idPress = self.canvas.mpl_connect('button_press_event', self.range_on_press)
                self._idDrag = self.canvas.mpl_connect('motion_notify_event', self.range_on_move)
                self._idRelease = self.canvas.mpl_connect(
                    'button_release_event', self.range_on_release)
                self.mode = 'eqlogbreak'
                self.color = 'r'
                self.canvas.widgetlock(self)
            else:
                self.canvas.widgetlock.release(self)
        self._update_buttons_checked()

    def _click_errorbarAction(self, flag):
        figure = self.canvas.figure
        for ax in figure.get_axes():
            errors = ax.lines
            for c in ax.collections:
                c.set_visible(flag)
            errors[1].set_visible(flag)
            errors[2].set_visible(flag)
        self.canvas.draw()

    def range_on_press(self, event):
        self.press_flag = True
        self.pressv = event.xdata
        trans = blended_transform_factory(event.inaxes.transData,
                                          event.inaxes.transAxes)
        w, h = 0, 1
        self.rect = Rectangle((0, 0), w, h,
                              transform=trans,
                              visible=False,
                              facecolor=self.color,
                              edgecolor=self.color,
                              alpha=self.alpha)
        event.inaxes.add_patch(self.rect)
        event.inaxes.figure.canvas.draw_idle()

    def range_on_move(self, event):
        ax = event.inaxes
        if ax not in self.canvas.figure.get_axes():
            if self.cursor_line:
                self.cursor_line.remove()
                self.cursor_line = None
                self.canvas.figure.canvas.draw_idle()
            return
        if self.press_flag:
            minv, maxv = sorted((event.xdata, self.pressv))
            self.rect.set_x(minv)
            self.rect.set_width(maxv - minv)
            self.rect.set_visible(True)
        else:
            self.cursor_motion(event)
        ax.figure.canvas.draw_idle()

    def range_on_release(self, event):
        self.press_flag = False
        if self.rect:
            self.RangeDrawEndSignal.emit(self.rect)

    def break_press(self, event):
        ax = event.inaxes
        line = ax.axvline(event.xdata, color=self.color)
        # self.cursor_line.remove()
        # self.cursor_line = None
        # self.canvas.draw()
        self.BreakLineDrawEndSignal.emit(line)
