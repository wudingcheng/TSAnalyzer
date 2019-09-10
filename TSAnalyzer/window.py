#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qtpy.QtWidgets import *
from qtpy.QtCore import Qt, QCoreApplication, QUrl
from qtpy.QtGui import QDesktopServices
import sys

from .widgets.timeseries_figure import TimeSeriesWidget
from .widgets.timeseries_toolbar import TimeSeriesToolBar
from .widgets.file_dockwidget import FileDockWidget
# from .widgets.discontinuity_dockwidget import DiscontinuityDockWidget
from .widgets.discontinuity_dock import DiscontinuitiesDockWidget
from .widgets.analysis_dockwidget import AnalysisDockWidget
from .widgets.console_dock import ConsoleDockWidget
from .widgets.about_dialog import AboutDialog
from .widgets.date_dialog import DateDialog
from .widgets.header_widget import FileHeaderWidget
from .models.reader import Reader
from .models.offsets import TSOffsetsHandler
from .contoller import TimeSeriesController, Controller, AnalysisController
from .utils import getIcon


def _(text, disambiguation=None, context='TSAnalyzerMainWindow'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class TSAnalyzerMainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("TSAnalyzer")
        self.setWindowIcon(getIcon('icon'))
        self.__initWidgets()
        self.__initToolBar()
        self.__initMenu()
        self.reader = Reader(self)
        self.offsetsHandler = TSOffsetsHandler()
        self.tsController = TimeSeriesController(self.reader,
                                                 self.offsetsHandler,
                                                 self.discontinuityDock,
                                                 self.timeSeriesToolBar,
                                                 self.timeSeriesWidget,
                                                 self.consoleDock)
        self.controller = Controller(self.reader,
                                     self.fileDockWidget,
                                     self.discontinuityDock,
                                     self.timeSeriesWidget,
                                     self.consoleDock,
                                     self.statusBar)

        self.analysisController = AnalysisController(self.fileDockWidget,
                                                     self.analysisDock,
                                                     self.consoleDock,
                                                     self.reader,
                                                     self.offsetsHandler,
                                                     self.timeSeriesWidget)

        self.resize(1000, 700)

    def __initWidgets(self):
        self.timeSeriesWidget = TimeSeriesWidget()
        self.setCentralWidget(self.timeSeriesWidget)

        # status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # file dock
        self.fileDockWidget = FileDockWidget(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.fileDockWidget)

        # discontinuity dock
        # self.discontinuityDock = DiscontinuityDockWidget(self)
        self.discontinuityDock = DiscontinuitiesDockWidget(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.discontinuityDock)

        # analysis dock
        self.analysisDock = AnalysisDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.analysisDock)

        # console dock
        self.consoleDock = ConsoleDockWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.consoleDock)

        # AboutDialog
        self.aboutDialog = AboutDialog(self)

        self.dateDialog = DateDialog(self)
        # self.dateDialog.setWindowIcon(getIcon('icon'))
        self.headerWidget = FileHeaderWidget()

    def __initMenu(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.fileMenu = self.menuBar.addMenu(_("&File"))
        self.toolMenu = self.menuBar.addMenu(_("&Tools"))
        self.aboutMenu = self.menuBar.addMenu(_("&About"))

        self.fileMenu.addActions(self.fileDockWidget.actions.values())
        self.fileMenu.addSeparator()
        self.fileMenu.addActions(self.discontinuityDock.actions.values())

        exitAction = QAction(_("Close"), self.fileMenu)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(exitAction)
        exitAction.triggered.connect(self.close)

        aboutAction = QAction(getIcon("icon"), _("About"), self.aboutMenu)
        homeAction = QAction(_("Home Page"), self.aboutMenu)
        bugAction = QAction(_("Suggestions and Bugs Report"), self.aboutMenu)
        self.aboutMenu.addAction(homeAction)
        self.aboutMenu.addAction(bugAction)
        self.aboutMenu.addSeparator()
        self.aboutMenu.addAction(aboutAction)
        homeAction.triggered.connect(self.slotHelpHomePage)
        aboutAction.triggered.connect(self.aboutDialog.show)

        # tool menu actions
        headerAction = QAction(_("Header Convert Tool"), self.toolMenu)
        dateAction = QAction(_("Date Calculator"), self.toolMenu)
        self.toolMenu.addAction(headerAction)
        self.toolMenu.addAction(dateAction)
        headerAction.triggered.connect(self.headerWidget.show)
        dateAction.triggered.connect(self.dateDialog.show)

        # self.toolMenu.addSeparator()
        # hectorAction = QAction(_("Format for Hector/CATS"), self.toolMenu)
        # self.toolMenu.addAction(hectorAction)

    def __initToolBar(self):
        self.timeSeriesToolBar = TimeSeriesToolBar(self.timeSeriesWidget.canvas, None)
        self.addToolBar(self.timeSeriesToolBar)

    def resizeEvent(self, event):
        self.timeSeriesWidget.adjustFigure()

    def slotHelpHomePage(self):
        QDesktopServices.openUrl(QUrl("https://github.com/wudingcheng/tsanalyzer"))

    def slotHelpBugs(self):
        QDesktopServices.openUrl(QUrl("https://github.com/wudingcheng/TSAnalyzer/issues"))


def main():
    import os
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    qss = os.path.join(os.path.dirname(__file__), 'resources/style.qss')
    with open(qss, 'r') as f:
        app.setStyleSheet(f.read())
    window = TSAnalyzerMainWindow()
    window.show()
    sys.exit(app.exec_())
