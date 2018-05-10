#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from ..utils import makeAction
from ..models.offsets import DISCONTINUITIES, DiscontinuityEvent
import os
from qtpy.QtGui import *
from qtpy.compat import getopenfilenames, getopenfilename, getsavefilename


def _(text, disambiguation=None, context='DiscontinuityDockWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class DiscontinuityWidget(QWidget):
    sig_discontinuity_updated = Signal(DiscontinuityEvent, DiscontinuityEvent)

    def __init__(self, discontinuity, parent=None):
        super(QWidget, self).__init__(parent=parent)
        self.setupUI()
        self.discontinuity = discontinuity
        self.displayDiscontinuity()
        self.connectSignals()

    def setupUI(self):
        layout = QHBoxLayout()
        self.component_label = QLabel("")
        self.date_edit = QDateEdit()
        self.combo = QComboBox()
        self.combo.addItems(DISCONTINUITIES.keys())
        self.tau_edit = QSpinBox()
        self.tau_edit.setMinimum(1)

        layout.addWidget(self.component_label)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.combo)
        layout.addWidget(self.tau_edit)

        self.date_edit.setCurrentSectionIndex(2)

        self.tau_edit.setVisible(False)
        self.setLayout(layout)

    def connectSignals(self):
        self.combo.currentTextChanged.connect(lambda text: self.tau_edit.setVisible('decay' in text))
        self.date_edit.dateChanged.connect(self.signalsOnChanged)
        self.combo.currentIndexChanged.connect(self.signalsOnChanged)
        self.tau_edit.valueChanged.connect(self.signalsOnChanged)

    def _pydate2qdate(self, date):
        return QDate(date.year, date.month, date.day)

    def displayDiscontinuity(self):
        self.blockSignals(True)
        self.component_label.setText(self.discontinuity.component)
        self.combo.setCurrentIndex(DISCONTINUITIES.keys().index(self.discontinuity.name))
        self.date_edit.setDate(self._pydate2qdate(self.discontinuity.date))
        tau = getattr(self.discontinuity, 'tau', None)
        if tau:
            self.tau_edit.setVisible(True)
            self.tau_edit.setValue(tau)
        self.blockSignals(False)

    def getDiscontinuityFromWidget(self):
        component = self.component_label.text()
        date = self.date_edit.date().toPyDate()
        name = self.combo.currentText()
        discontinuity = DISCONTINUITIES[name](date, component)
        if self.tau_edit.isVisible():
            discontinuity.tau = self.tau_edit.value()
        return discontinuity

    def signalsOnChanged(self):
        discontinuity = self.getDiscontinuityFromWidget()
        if discontinuity.name == self.discontinuity.name:
            self.discontinuity.date = discontinuity.date
        else:
            discontinuity.line = self.discontinuity.line
            self.sig_discontinuity_updated.emit(self.discontinuity, discontinuity)
            self.discontinuity = discontinuity
            self.displayDiscontinuity()
        self.discontinuity.statusChanged()


class DiscontinuityDockWidget(QDockWidget):
    sig_discontinuity_removed = Signal(DiscontinuityEvent)
    sig_discontinuity_updated = Signal(DiscontinuityEvent, DiscontinuityEvent)
    sig_discontinuity_file_imported = Signal(str)
    sig_discontinuity_file_exported = Signal(str)

    def __init__(self, parent=None):
        super(DiscontinuityDockWidget, self).__init__(parent=parent)
        self.setWindowTitle(_("Discontinuity File"))
        self._discontinuities = {}
        self.__initWidgets()
        self.__initActions()

    def __initWidgets(self):
        widget = QWidget()
        self.setWidget(widget)
        layout = QVBoxLayout(widget)
        self.discontinuitiesWidget = QListWidget()
        layout.addWidget(self.discontinuitiesWidget)

        self.menu = QMenu(self)

    def __initActions(self):
        _actions = [
            (self, _('Import Discontinuities'), _("Import Discontinuities File"),
             self.slotOnImportDiscontinuities, "Import", None, False),
            (self, _('Remove Discontinuities'), _("Remove Discontinuities"),
             self.slotOnDeleteDiscontinuities, "remove", None, False),
            (self, _('Clear Discontinuities'), _("Clear Discontinuities"),
             self.slotOnClearDiscontinuities, "discontinuities.clear", None, False),
            None,
            (self, _('Export Discontinuities'), _("Export Discontinuities"),
             self.slotOnExportDiscontinuities, "Export", None, False),
        ]
        self.actions = {}
        for act in _actions:
            if act is not None:
                a = makeAction(*act)
                self.menu.addAction(a)
                self.actions[act[-3]] = a
            else:
                self.menu.addSeparator()

    def addDiscontinuity(self, discontinuity):
        item = DiscontinuityWidget(discontinuity)
        # item.sig_discontinuity_updated.connect(self.sigiscontinuity_updated.emit)
        listItem = QListWidgetItem(self.discontinuitiesWidget)
        listItem.setSizeHint(item.sizeHint())
        self.discontinuitiesWidget.addItem(listItem)
        self.discontinuitiesWidget.setItemWidget(listItem, item)
        self._discontinuities[discontinuity] = [item, listItem]
        self._discontinuities[discontinuity][0].sig_discontinuity_updated.connect(self._updateDiscontinutityInWidget)

    def _updateDiscontinutityInWidget(self, old, new):
        print('_update', old, new)
        item, listItem = self._discontinuities[old]
        item.displayDiscontinuity()
        self._discontinuities[new] = [item, listItem]
        self._discontinuities.pop(old)
        self.sig_discontinuity_updated.emit(old, new)

    def addDiscontinuities(self, discontinuities):
        for discontinuity in discontinuities:
            self.addDiscontinuity(discontinuity)

    def updateDiscontinuity(self, discontinuity):
        item = self._discontinuities.pop(discontinuity, None)
        if item:
            discontinuity.lineMoved()
            item[0].displayDiscontinuity()
            self._discontinuities[discontinuity] = item

    def removeDiscontinuity(self, discontinuity):
        item = self._discontinuities.get(discontinuity, None)
        if item:
            self.discontinuitiesWidget.removeItemWidget(item[1])
            self.discontinuitiesWidget.takeItem(self.discontinuitiesWidget.row(item[1]))
            try:
                item[0].deleteLater()
            except RuntimeError:
                pass

    def clearDiscontinuities(self):
        self.discontinuitiesWidget.clear()
        self._discontinuities = {}

    def slotOnImportDiscontinuities(self):
        filename = getopenfilename(self,
                                   'Choose Offsets file',
                                   '',
                                   self.tr('*.json'),
                                   None,
                                   QFileDialog.DontUseNativeDialog)[0]
        self.sig_discontinuity_file_imported.emit(filename)

    def slotOnExportDiscontinuities(self):
        filename = getsavefilename(self,
                                   "Save discontinuities into file",
                                   "",
                                   self.tr("*.json"),
                                   None,
                                   QFileDialog.DontUseNativeDialog)[0]
        if filename:
            self.sig_discontinuity_file_exported.emit(filename)

    def setDiscontinuityInCurrent(self, discontinuity):
        item = self._discontinuities.get(discontinuity, None)
        if item:
            self.discontinuitiesWidget.setCurrentItem(item[1])

    def slotOnDeleteDiscontinuities(self):
        item = self.discontinuitiesWidget.currentItem()
        widget = self.discontinuitiesWidget.itemWidget(item)
        for discontinuity, value in self._discontinuities.items():
            if value == [widget, item]:
                self.sig_discontinuity_removed.emit(discontinuity)

    def slotOnClearDiscontinuities(self):
        for discontinuity, value in self._discontinuities.items():
            self.sig_discontinuity_removed.emit(discontinuity)

    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
