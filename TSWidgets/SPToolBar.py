from PyQt4.QtGui import QAction, QIcon

from NavigationToolBar import NavigationToolbar


class SPToolBar(NavigationToolbar):

    def __init__(self, canvas, parent, coordinates=True):
        self._idPick = None
        self.point_cursor = None
        self.annotation = None
        self.line = None
        super(SPToolBar, self).__init__(canvas, parent, coordinates=True)

    def _init_toolbar(self):
        super(SPToolBar, self)._init_toolbar()
        self.logAction = QAction(QIcon(":/TSResource/images/log.png"), "Log", self)
        self.logAction.setToolTip("Logarithic axises")
        self.logAction.setCheckable(True)
        self.addAction(self.logAction)
        self.legendAction = QAction(QIcon(":/TSResource/images/legend_pick.png"), "Items", self)
        self.legendAction.setToolTip("Click legend to set item visible")
        self.legendAction.setCheckable(True)
        self.addAction(self.legendAction)

        self.annotationAction = QAction(
            QIcon(":/TSResource/images/tooltip.png"), "Annotation", self)
        self.annotationAction.setToolTip("Show annotation")
        self.annotationAction.setCheckable(True)
        self.addAction(self.annotationAction)

        self.logAction.triggered.connect(self._click_logAction)
        self.legendAction.triggered.connect(self._click_legendAction)
        self.annotationAction.triggered.connect(self._click_annotationAction)

    def _click_logAction(self, flag):
        for ax in self.canvas.figure.get_axes():
            if flag:
                ax.set_xscale("log", nonposx='clip')
                ax.set_yscale("log", nonposy='clip')
                ax.relim()
            else:
                ax.set_xscale("linear")
                ax.set_yscale("linear")
            self.canvas.draw_idle()

    def _click_legendAction(self, flag):
        if flag:
            self.legend_pickable_connection()
        else:
            self.legend_pickable_disconnection()

    def _click_annotationAction(self, flag):
        if not flag and self.annotation:
            self.annotation.remove()
            self.annotation = None
            self.canvas.draw_idle()

    def legend_pickable_connection(self):
        if self._idPress is not None:
            self.canvas.mpl_disconnect(self._idPress)
        if self._idRelease is not None:
            self.canvas.mpl_disconnect(self._idRelease)
        if self._idDrag is not None:
            self.canvas.mpl_disconnect(self._idDrag)
        self._idPress = self.canvas.mpl_connect("button_press_event", self.highlight_press)
        self._idDrag = self.canvas.mpl_connect(
            "motion_notify_event", self.legend_on_hover)

    def legend_pickable_disconnection(self):
        self._idPick = self.canvas.mpl_disconnect(self._idPick)
        self._idDrag = self.canvas.mpl_disconnect(self._idDrag)
        if self.annotation:
            self.annotation = self.annotation.remove()
        for ax in self.canvas.figure.get_axes():
            for line in ax.lines:
                if line.get_linewidth() != 1.0:
                    line.set_linewidth(1.0)
                if line.get_alpha() != 1.0:
                    line.set_alpha(1.0)
        self.canvas.draw_idle()

    def legend_on_hover(self, event):
        ax = event.inaxes
        if ax not in self.canvas.figure.get_axes():
            return
        for line in ax.lines:
            res = line.contains(event)
            if res[0]:
                self.line = line
                self.highlight(ax, line)
                if self.annotationAction.isChecked():
                    x, y = line.get_xydata()[res[1]['ind'][0]]
                    label = ax.get_xlabel() if ax.get_xlabel() else 'x ='
                    ylabel = ax.get_ylabel() if ax.get_ylabel() else 'y ='
                    if self.annotation:
                        self.annotation.set_visible(True)
                        self.annotation.xy = x, y
                        self.annotation.set_position = (x, y)
                        self.annotation.set_text("%s %.4f\n%s %.4f" % (label, x, ylabel, y))
                    else:
                        self.annotation = ax.annotate(("%s %.4f\n%s %.4f" % (label, x, ylabel, y)),
                                                      xy=(x, y), xycoords='data',
                                                      xytext=(x + 20, y), textcoords='offset points',
                                                      ha='left', va='bottom', fontsize=10,
                                                      color="white", zorder=10,
                                                      bbox=dict(boxstyle='square',
                                                                fc='grey', alpha=1, ec='grey'),
                                                      arrowprops=dict(arrowstyle='->', color='grey',
                                                                      connectionstyle='arc3,rad=0'))
                break
            else:
                if self.annotation:
                    self.annotation.set_visible(False)
                self.highlight(ax, None)

    def highlight(self, ax, target):
        need_redraw = False
        if target is None:
            for line in ax.lines:
                if line.get_linewidth() != 1.0:
                    line.set_linewidth(1.0)
                    need_redraw = True
        else:
            for line in ax.lines:
                if line == target:
                    line.set_linewidth(2.0)
                    need_redraw = True
        if need_redraw:
            self.canvas.draw_idle()

    def highlight_press(self, event):
        ax = event.inaxes
        for line in ax.lines:
            if line == self.cursor_line:
                continue
            if line == self.line and self.line:
                line.set_alpha(1.0)
            else:
                line.set_alpha(0.2)
        # ax.legend(loc='best')
        self.canvas.draw()
