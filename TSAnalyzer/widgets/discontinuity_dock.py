#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from ..utils import makeAction
from ..models.offsets import DISCONTINUITIES, DiscontinuityEvent
from qtpy.compat import getopenfilename, getsavefilename
from qtpy.uic import loadUi
import os


class DiscontinuityTreeItem(QTreeWidgetItem):

    sig_discontinuity_updated = Signal(DiscontinuityEvent, DiscontinuityEvent)

    def __init__(self, discontinuity, parent):
        super(DiscontinuityTreeItem, self).__init__(parent)
        self.parent = parent
        self.discontinuity = discontinuity
        self.setDiscontinuityText()
        self.setup()

    def _pydate2qdate(self, date):
        return QDate(date.year, date.month, date.day)

    def addItemWidget(self, text, widget):
        item = QTreeWidgetItem(self)
        item.setText(0, text)
        self.parent.setItemWidget(item, 1, widget)
        self.addChild(item)
        return item

    def setup(self):
        for i in reversed(range(self.childCount())):
            self.removeChild(self.child(i))

        self.dateEdit = QDateEdit()
        self.dateEdit.setDate(self._pydate2qdate(self.discontinuity.date))
        self.addItemWidget("Date", self.dateEdit)
        self.dateEdit.dateChanged.connect(self.slotOnPropertiesChanged)

        self.combo = QComboBox()
        self.combo.addItems(DISCONTINUITIES.keys())
        self.combo.setCurrentText(self.discontinuity.name)
        self.addItemWidget("Type", self.combo)
        self.combo.currentTextChanged.connect(self.slotOnPropertiesChanged)

        self.tauSpin = QSpinBox()
        self.tauSpin.setMinimum(1)
        self.tauItem = self.addItemWidget("Tau", self.tauSpin)
        tau = getattr(self.discontinuity, 'tau', None)
        if tau:
            self.tauSpin.setValue(tau)
            self.tauItem.setHidden(False)
        else:
            self.tauItem.setHidden(True)
        self.tauSpin.valueChanged.connect(self.slotOnPropertiesChanged)

    def getDiscontinuityFromItems(self):
        component = self.discontinuity.component
        date = self.dateEdit.date().toPyDate()
        name = self.combo.currentText()
        self.tauItem.setHidden(name in ('offset', 'trendchange'))
        discontinuity = DISCONTINUITIES[name](date, component)
        if not self.tauItem.isHidden():
            discontinuity.tau = self.tauSpin.value()
        return discontinuity

    def setDiscontinuityText(self):
        self.setText(0, self.discontinuity.dateStr())
        self.setText(1, "{} {}".format(self.discontinuity.component,
                                       self.discontinuity.name))
        self.setToolTip(1, str(self.discontinuity))

    def slotOnPropertiesChanged(self):
        obj = self.getDiscontinuityFromItems()
        if self.discontinuity.name == obj.name:
            self.discontinuity.date = obj.date
        else:
            obj.line = self.discontinuity.line
            # self.sig_discontinuity_updated.emit(self.discontinuity, obj)
            self.treeWidget().sig_discontinuity_updated.emit(self.discontinuity, obj)
            self.discontinuity = obj
        self.discontinuity.statusChanged()
        self.setDiscontinuityText()

    def slotOnDiscontinuityChanged(self, discontinuity):
        self.discontinuity = discontinuity
        self.setup()
        self.setDiscontinuityText()


class DiscontinuityTreeWidget(QTreeWidget):

    sig_discontinuity_removed = Signal(DiscontinuityEvent)
    sig_discontinuity_updated = Signal(DiscontinuityEvent, DiscontinuityEvent)
    sig_discontinuity_file_imported = Signal(str)
    sig_discontinuity_file_exported = Signal(str)

    def __init__(self, parent=None):
        super(DiscontinuityTreeWidget, self).__init__(parent=parent)
        self._discontinuities = {}
        self.setSortingEnabled(True)
        self.setColumnCount(2)
        self.setHeaderLabels(["Name", "Value"])
        self.sig_discontinuity_updated.connect(self.slotOnDiscontinuityUpdated)

    def slotOnDiscontinuityUpdated(self, old, new):
        item = self._discontinuities.pop(old)
        self._discontinuities[new] = item

    def addDiscontinuity(self, discontinuity):
        item = DiscontinuityTreeItem(discontinuity, self)
        self._discontinuities[discontinuity] = item

    def addDiscontinuities(self, discontinuities):
        for discontinuity in discontinuities:
            self.addDiscontinuity(discontinuity)

    def updateDiscontinuity(self, discontinuity):
        item = self._discontinuities.pop(discontinuity, None)
        if item:
            discontinuity.lineMoved()
            item.slotOnDiscontinuityChanged(discontinuity)
            self._discontinuities[discontinuity] = item

    def removeDiscontinuity(self, discontinuity):
        item = self._discontinuities.pop(discontinuity, None)
        if item:
            root = self.invisibleRootItem()
            root.removeChild(item)

    def setDiscontinuitiesVisible(self, text):
        if text == 'All':
            for _, item in self._discontinuities.items():
                item.setHidden(False)
            return
        obj = DISCONTINUITIES[text]
        for discontinuity, item in self._discontinuities.items():
            flag = not isinstance(discontinuity, obj)
            item.setHidden(flag)

    def clearDiscontinuities(self):
        # for discontinuity, item in self._discontinuities.items():
        #     flag = item.isHidden()
        #     if not flag:
        #         self.removeDiscontinuity(discontinuity)
        self.clear()
        self._discontinuities = {}

    def collapseAll(self):
        for item in self._discontinuities.values():
            self.collapseItem(item)

    def expandDiscontinuity(self, discontinuity):
        self.collapseAll()
        item = self._discontinuities.get(discontinuity, None)
        if item:
            self.expandItem(item)

    def slotOnImportDiscontinuities(self):
        filename = getopenfilename(self,
                                   'Choose Offsets file',
                                   '',
                                   self.tr('*.json'),
                                   None,
                                   QFileDialog.DontUseNativeDialog)[0]
        if filename:
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

    def slotOnDeleteDiscontinuities(self):
        item = self.currentItem()
        if isinstance(item, DiscontinuityTreeItem):
            discontinuity = self.currentItem().discontinuity
            self.removeDiscontinuity(discontinuity)
            self.sig_discontinuity_removed.emit(discontinuity)

    def slotOnClearDiscontinuities(self):
        for discontinuity in list(self._discontinuities):
            item = self._discontinuities[discontinuity]
            if not item.isHidden():
                self.sig_discontinuity_removed.emit(discontinuity)
        # for discontinuity, item in self._discontinuities.items():
        #     if not item.isHidden():
        #         self.sig_discontinuity_removed.emit(discontinuity)


def _(text, disambiguation=None, context='DiscontinuitiesDock'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class DiscontinuitiesDockWidget(QDockWidget):
    sig_discontinuity_removed = Signal(DiscontinuityEvent)
    sig_discontinuity_updated = Signal(DiscontinuityEvent, DiscontinuityEvent)
    sig_discontinuity_file_imported = Signal(str)
    sig_discontinuity_file_exported = Signal(str)
    sig_discontinuity_visible = Signal(str)

    def __init__(self, parent=None):
        super(DiscontinuitiesDockWidget, self).__init__(parent=parent)
        self.setWindowTitle(_("Discontinuities"))
        self.__initWidgets()
        self.__initActions()
        self.__initSignals()

    def __initWidgets(self):
        self.widget = QWidget()
        ui = os.path.join(os.path.dirname(__file__), "../resources/ui/discontinuity.ui")
        loadUi(ui, self.widget)
        self.discontinuityTreeWidget = DiscontinuityTreeWidget()
        self.widget.layout().insertWidget(1, self.discontinuityTreeWidget)
        # self.setWidget(self.discontinuityTreeWidget)
        self.setWidget(self.widget)
        self.menu = QMenu(self)

        # combo additems
        self.widget.comboBox.addItems(["All"] + list(DISCONTINUITIES.keys()))
        self.widget.comboBox.currentTextChanged.connect(self.slotOnVisibleDiscontinuities)

    def __initActions(self):
        _actions = [
            (self, _('Import Discontinuities'), _("Import Discontinuities File"),
             self.discontinuityTreeWidget.slotOnImportDiscontinuities, "Import", None, False),
            (self, _('Remove Current Discontinuities'), _("Remove Current Discontinuities"),
             self.discontinuityTreeWidget.slotOnDeleteDiscontinuities, "remove", None, False),
            (self, _('Clear Discontinuities'), _("Clear All Discontinuities"),
             self.discontinuityTreeWidget.slotOnClearDiscontinuities, "discontinuities.clear", None, False),
            None,
            (self, _('Export Discontinuities'), _("Export Discontinuities"),
             self.discontinuityTreeWidget.slotOnExportDiscontinuities, "Export", None, False),
        ]
        self.actions = {}
        for act in _actions:
            if act is not None:
                a = makeAction(*act)
                self.menu.addAction(a)
                self.actions[act[-3]] = a
            else:
                self.menu.addSeparator()

    def __initSignals(self):
        self.discontinuityTreeWidget.sig_discontinuity_removed.connect(self.sig_discontinuity_removed)
        self.discontinuityTreeWidget.sig_discontinuity_updated.connect(self.sig_discontinuity_updated)
        self.discontinuityTreeWidget.sig_discontinuity_file_imported.connect(self.sig_discontinuity_file_imported)
        self.discontinuityTreeWidget.sig_discontinuity_file_exported.connect(self.sig_discontinuity_file_exported)

    def slotOnVisibleDiscontinuities(self, text):
        self.sig_discontinuity_visible.emit(text)
        self.actions['discontinuities.clear'].setText(_("Clear {} Discontinuities".format(text.title())))
        self.discontinuityTreeWidget.setDiscontinuitiesVisible(text)

    def setDiscontinuityInCurrent(self, discontinuity):
        self.discontinuityTreeWidget.expandDiscontinuity(discontinuity)

    def clearDiscontinuities(self):
        self.discontinuityTreeWidget.clearDiscontinuities()

    def addDiscontinuity(self, discontinuity):
        self.discontinuityTreeWidget.addDiscontinuity(discontinuity)

    def addDiscontinuities(self, discontinuities):
        self.discontinuityTreeWidget.addDiscontinuities(discontinuities)

    def updateDiscontinuity(self, discontinuity):
        self.discontinuityTreeWidget.updateDiscontinuity(discontinuity)

    def removeDiscontinuity(self, discontinuity):
        self.discontinuityTreeWidget.removeDiscontinuity(discontinuity)

    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
