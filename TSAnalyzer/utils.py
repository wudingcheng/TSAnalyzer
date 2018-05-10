#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from qtpy.QtGui import QIcon, QKeySequence
from qtpy.QtWidgets import QAction
import textwrap

_iconcache = {}
base_dir = os.path.join(os.path.dirname(__file__), 'resources/images')


def getIcon(icon):
    if icon not in _iconcache:
        filename = os.path.join(base_dir, icon + '.png')
        _iconcache[icon] = QIcon(filename)
    return _iconcache[icon]


def makeAction(parent, descr, menutext, slot, icon=None, key=None, checkable=False):
    a = QAction(parent)
    a.setText(menutext)
    a.setStatusTip(descr)
    a.setToolTip(textwrap.fill(descr, 25))
    if slot:
        a.triggered.connect(slot)
    if icon:
        a.setIcon(getIcon(icon))
    if key:
        a.setShortcut(QKeySequence(key))
    if checkable:
        a.setCheckable(True)
    return a
