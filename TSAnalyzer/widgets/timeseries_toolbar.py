#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from ..models.offsets import DISCONTINUITIES, DiscontinuityEvent
from ..utils import makeAction


def _(text, disambiguation=None, context='TimeSeriesToolBar'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class TimeSeriesToolBar(NavigationToolbar):
    sig_discontinuity_triggered = Signal(str, bool)
    _actionValidation = ['pan', 'zoom']

    def __init__(self, canvas, parent):
        super(TimeSeriesToolBar, self).__init__(canvas, parent, True)
        self.setWindowTitle("Time Series ToolBar")

    def _getDiscontinuitiesActions(self):
        actions = []
        for key, item in DISCONTINUITIES.items():
            actions.append((
                self,
                _(item.getDescription()),
                _(item.getName()),
                self.slotOnDiscontinuityTriggered,
                item.getIcon(),
                item.key,
                True)
            )
            self._actionValidation.append(key)
        return actions

    def _init_toolbar(self):
        _actions = [
            (self, _('Reset original view'), _('Home'), self.home, 'home', "alt+h", False),
            (self, _('Back to previous view'), _('Back'), self.back, 'back', None, False),
            (self, _('Forward to next view'), _('Forward'), self.forward, 'forward', None, False),
            None,
            (self, _('Pan axes with left mouse'), _('Pan'), self.pan, 'pan', "alt+p", True),
            (self, _('Zoom to rectangle'), _('Zoom'), self.zoom, 'zoom', "alt+z", True),
            (self, _('Configure subplots'), _('Subplots'), self.configure_subplots, 'subplots', None, False),
            (self, _('Axes editor'), _('Axes'), self.edit_parameters, 'options', None, False),
            None,
            None,
            (self, _('Save the figure'), _('Save'), self.save_figure, 'save', "alt+s", False)]
        _actions[-2:-2] = self._getDiscontinuitiesActions()
        self._actions = {}
        for act in _actions:
            if act is not None:
                a = makeAction(*act)
                self.addAction(a)
                self._actions[act[-3]] = a
            else:
                self.addSeparator()
        self.locLabel = QLabel("", self)
        self.locLabel.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.locLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored))
        self.addWidget(self.locLabel)

    def set_message(self, s):
        pass
        # self.locLabel.setText(s)

    def slotOnDiscontinuityTriggered(self, flag):
        discontinuity = self.sender().text()
        if self._active == discontinuity.upper():
            self._active = None
            self.mode = ''
        else:
            self._active = discontinuity.upper()
            self.mode = discontinuity

        if flag:
            self.canvas.setCursor(Qt.CrossCursor)
            self.canvas.widgetlock.release(self)
        else:
            self.canvas.setCursor(Qt.ArrowCursor)
            self.canvas.widgetlock(self)

        self._update_buttons_checked()
        self.sig_discontinuity_triggered.emit(discontinuity,
                                              self._actions[discontinuity].isChecked())

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for key in self._actionValidation:
            self._actions[key].setChecked(self._active == key.upper())
