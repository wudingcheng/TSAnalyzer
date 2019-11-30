#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .models.offsets import DISCONTINUITIES
from .thread.fit_thread import TSOutliersThread, TSFitThread
from .thread.l1_thread import TSL1Thread
from .widgets.batch_widget import L1BatchWidget, FitBatchWidget
from qtpy.compat import getsavefilename
from qtpy.QtWidgets import QFileDialog


class Controller(object):
    def __init__(self,
                 reader,
                 fileDockWidget,
                 discontinuityDock,
                 timeSeriesWidget,
                 consoleDock,
                 statusBar):
        """
        :param fileDockWidget: .widgets.file_dockwidget.FileDockWidget
        :param timeSeriesWidget: .widgets.timesereis_figure.TimeSeriesWidget
        """
        self.fileDockWidget = fileDockWidget
        self.discontinuityDock = discontinuityDock
        self.timeSeriesWidget = timeSeriesWidget
        self.reader = reader
        self.consoleDock = consoleDock
        self.statusBar = statusBar
        self._setup()

    def _setup(self):
        self.fileDockWidget.sig_file_loaded.connect(self.slotOnFileLoaded)
        self.fileDockWidget.sig_file_removed.connect(self.slotOnFileRemoved)
        self.reader.sig_file_read.connect(lambda: self.timeSeriesWidget.slotOnDataLoaded(self.reader))

    def slotOnFileLoaded(self, filename):
        try:
            self.reader.readFile(filename)
            self.statusBar.showMessage("Working: {}".format(filename))
        except Exception as ex:
            self.consoleDock.slotOnShowErrors(str(ex))

    def slotOnFileRemoved(self):
        self.reader.clear()
        # self.discontinuityDock.updateDiscontinuity()
        self.discontinuityDock.clearDiscontinuities()
        self.statusBar.clearMessage()
        self.timeSeriesWidget.figure.clear()
        self.timeSeriesWidget.canvas.draw_idle()


class TimeSeriesController(object):
    def __init__(self,
                 reader,
                 offsetsHandler,
                 discontinuityDock,
                 toolbar,
                 timeSeriesWidget,
                 consoleDock):
        self.reader = reader
        self.offsetsHandler = offsetsHandler
        self.discontinuityDock = discontinuityDock
        self.toolbar = toolbar
        self.timeSeriesWidget = timeSeriesWidget
        self.consoleDock = consoleDock
        self._setup()

    def _setup(self):
        self.toolbar.sig_discontinuity_triggered.connect(self.slotOnDiscontinuityTriggered)
        self.timeSeriesWidget.sig_message_update.connect(self.toolbar.locLabel.setText)
        self.timeSeriesWidget.sig_discontinuity_added.connect(self.slotOnDiscontinuityAdded)
        self.timeSeriesWidget.sig_discontinuity_removed.connect(self.slotOnDiscontinuityRemoved)
        self.timeSeriesWidget.sig_discontinuity_moved.connect(self.slotOnDiscontinuityMoved)
        self.timeSeriesWidget.sig_discontinuity_hovered.connect(self.discontinuityDock.setDiscontinuityInCurrent)
        self.timeSeriesWidget.sig_discontinuity_visibled.connect(self.slotOnDiscontinuitiesVisibled)
        self.timeSeriesWidget.sig_files_plotted.connect(self.slotOnUpdateSiteDiscontinuities)

        self.discontinuityDock.sig_discontinuity_removed.connect(self.slotOnDiscontinuityRemoved)
        self.discontinuityDock.sig_discontinuity_file_imported.connect(self.slotOnDiscontinuitiesFileImported)
        self.discontinuityDock.sig_discontinuity_file_exported.connect(self.slotOnDiscontinuitiesFileExported)
        self.discontinuityDock.sig_discontinuity_updated.connect(self.slotOnDiscontinuityUpdate)
        self.discontinuityDock.sig_discontinuity_visible.connect(self.slotOnDiscontinuityVisible)

    def slotOnDiscontinuitiesVisibled(self):
        self.discontinuityDock.widget.comboBox.setCurrentText("All")
        self.discontinuityDock.discontinuityTreeWidget.setDiscontinuitiesVisible("All")

    def slotOnDiscontinuityUpdate(self, oldDiscontinuity, newDiscontinuity):
        """Update discontinuity in DiscontinuityWidget
        :param oldDiscontinuity:
        :param newDiscontinuity:
        :return: None
        """
        self.offsetsHandler.updateDiscontinuity(self.reader.name, oldDiscontinuity, newDiscontinuity)
        self.timeSeriesWidget.discontinuityLines[newDiscontinuity.line] = newDiscontinuity

    def slotOnDiscontinuitiesFileImported(self, filename):
        if filename:
            try:
                self.offsetsHandler.fromJSONFile(filename)
                self.slotOnUpdateSiteDiscontinuities()
                self.consoleDock.slotOnShowLog("{} discontinuities imported.".format(filename))
            except Exception as ex:
                self.consoleDock.slotOnShowErrors(str(ex))

    def slotOnDiscontinuitiesFileExported(self, filename):
        try:
            self.offsetsHandler.saveToJSONFile(filename)
            self.consoleDock.slotOnShowLog("Discontinuities were written in {}".format(filename))
        except Exception as ex:
            self.consoleDock.slotOnShowErrors(str(ex))

    def slotOnUpdateSiteDiscontinuities(self):
        if self.reader.name is None:
            return
        discontinuities = self.offsetsHandler.getSiteOffsets(self.reader.name)
        self.discontinuityDock.clearDiscontinuities()
        self.discontinuityDock.addDiscontinuities(discontinuities)
        for discontinuity in discontinuities:
            if discontinuity.line not in self.timeSeriesWidget.discontinuityLines:
                ax = self.timeSeriesWidget.componentsAxes[discontinuity.component]
                line = ax.axvline(discontinuity.date, color=discontinuity.getColor(), linewidth=1, picker=3)
                discontinuity.line = line
                self.timeSeriesWidget.discontinuityLines[line] = discontinuity
        self.timeSeriesWidget.slotOnVisibleDiscontinuities(
            self.timeSeriesWidget.actions['figure.discontinuity'].isChecked())
        self.timeSeriesWidget.adjustFigure()

    def slotOnDiscontinuityTriggered(self, mode, flag):
        self.timeSeriesWidget.cursor_enabled = flag
        self.timeSeriesWidget.setCursorsColor(DISCONTINUITIES[mode].getColor())

    def slotOnDiscontinuityRemoved(self, discontinuity):
        self.offsetsHandler.removeDiscontinuity(self.reader.name, discontinuity)
        self.discontinuityDock.removeDiscontinuity(discontinuity)
        self.timeSeriesWidget.canvas.draw_idle()
        self.consoleDock.slotOnShowLog("{} removed.".format(discontinuity))

    def slotOnDiscontinuityMoved(self, discontinuity):
        self.discontinuityDock.updateDiscontinuity(discontinuity)

    def slotOnDiscontinuityVisible(self, text):
        self.timeSeriesWidget.setDiscontinuitiesVisible(text)

    def _validateDiscontinuity(self, date, component, mode):
        dates = self.reader.df.index
        flag = dates[0].to_pydatetime() < date and dates[-1].to_pydatetime()
        offsets = self.offsetsHandler.getSiteOffsets(self.reader.name)
        dates = [i.date for i in offsets if i.component == component and i.name == mode]
        interval = [abs(d - date).total_seconds() for d in dates]
        if interval:
            if min(interval) > 86400 * 3:
                flag2 = True
            else:
                flag2 = False
        else:
            flag2 = True
        return flag and flag2

    def slotOnDiscontinuityAdded(self, date, ax):
        if not self.toolbar.mode in DISCONTINUITIES:
            return
        if not self._validateDiscontinuity(date, ax.get_ylabel(), self.toolbar.mode):
            return
        discontinuity = DISCONTINUITIES[self.toolbar.mode]
        color = discontinuity.getColor()
        line = ax.axvline(date, color=color, linewidth=1, picker=3)
        discontinuity = discontinuity(date, ax.get_ylabel(), line=line)
        self.timeSeriesWidget.discontinuityLines[line] = discontinuity
        self.offsetsHandler.addDiscontinuity(self.reader.name, discontinuity)
        self.discontinuityDock.addDiscontinuity(discontinuity)
        self.consoleDock.slotOnShowLog("{} added.".format(discontinuity))


class AnalysisController(object):
    def __init__(self,
                 fileDock,
                 analysisDock,
                 consoleDock,
                 reader,
                 offsetsHandler,
                 timeSeriesWidget):
        self.fileDock = fileDock
        self.analysisDock = analysisDock
        self.consoleDock = consoleDock
        self.reader = reader
        self.offsetsHandler = offsetsHandler
        self.timeSeriesWidget = timeSeriesWidget
        self.dataAnalysisResult = {}
        self.__setup()

    def __setup(self):
        self.reader.sig_file_read.connect(self.slotOnRead)
        self.reader.sig_file_clear.connect(self.slotOnClear)

        self.analysisDock.sig_outliers_clicked.connect(self.slotOnOutliers)
        self.analysisDock.sig_fit_clicked.connect(self.slotOnFit)
        self.analysisDock.sig_fit_batch.connect(self.slotOnBatchClicked)
        self.analysisDock.sig_l1_clicked.connect(self.slotOnL1Clicked)
        self.analysisDock.sig_l1_batch.connect(self.slotOnBatchClicked)
        self.analysisDock.sig_data_saved.connect(self.slotOnSaveData)
        # self.analysisDock.sig_data_changed.connect(self.slotOnDataComboCurrentTextChanged)
        self.analysisDock.sig_data_changed.connect(self.slotOnDataChoosed)

    def slotOnRead(self):
        self.analysisDock.stack.setEnabled(True)
        self.dataAnalysisResult = {}

    def slotOnClear(self):
        self.analysisDock.stack.setEnabled(False)
        self.dataAnalysisResult = {}

    def slotOnSaveData(self):
        text = self.analysisDock.tsAnalysisWidget.dataCombo.currentText()
        data = self.dataAnalysisResult.get(text, None)
        if data is not None:
            filename = getsavefilename(self.analysisDock,
                                       "Save data into file",
                                       "",
                                       "*.dat",
                                       None,
                                       QFileDialog.DontUseNativeDialog)[0]
            if filename:
                self.reader.saveTODAT(data, filename)

    def slotOnOutliers(self, parameters):
        self.outliersThread = TSOutliersThread(self.analysisDock)
        self.outliersThread.sig_log.connect(self.consoleDock.slotOnShowLog)
        self.outliersThread.sig_error.connect(self.consoleDock.slotOnShowErrors)
        self.outliersThread.finished.connect(self.slotOnOutliersEnd)
        self.outliersThread.render(self.reader, self.offsetsHandler, parameters)
        self.outliersThread.start()

    def slotOnOutliersEnd(self):
        self.dataAnalysisResult['clean'] = self.reader.df
        self.analysisDock.tsAnalysisWidget.dataCombo.setCurrentText("clean")
        self.slotOnDataComboCurrentTextChanged()

    def slotOnFit(self, parameters):
        self.fitThread = TSFitThread(self.analysisDock)
        self.fitThread.sig_log.connect(self.consoleDock.slotOnShowLog)
        self.fitThread.sig_error.connect(self.consoleDock.slotOnShowErrors)
        self.fitThread.sig_fit_end.connect(self.slotOnFitEnd)
        self.fitThread.render(self.reader, self.offsetsHandler, parameters)
        self.fitThread.start()

    def slotOnFitEnd(self, args):
        self.analysisDock.tsAnalysisWidget.setDataWidgetVisible(True)
        self.dataAnalysisResult.update(args)
        self.analysisDock.tsAnalysisWidget.dataCombo.setCurrentText('fit')
        self.slotOnDataComboCurrentTextChanged()

    def slotOnDataComboCurrentTextChanged(self):
        text = self.analysisDock.tsAnalysisWidget.dataCombo.currentText()
        task = 'residuals' if text != 'fit' else 'fit'
        df = self.dataAnalysisResult.get(text, None)
        if df is not None:
            self.timeSeriesWidget.slotOnFitOrResiduals(df, self.reader.columns, task)

    def slotOnDataChoosed(self, text):
        
        df = self.dataAnalysisResult.get(text, None)
        if df is not None:
            self.timeSeriesWidget.slotOnFitOrResiduals(df, self.reader.columns, text)

    def slotOnL1Clicked(self, parameters):
        self.l1Thread = TSL1Thread(self.analysisDock)
        self.l1Thread.sig_log.connect(self.consoleDock.slotOnShowLog)
        self.l1Thread.sig_error.connect(self.consoleDock.slotOnShowErrors)
        self.l1Thread.sig_l1_end.connect(self.slotOnL1End)
        self.l1Thread.render(self.reader, parameters)
        self.l1Thread.start()

    def slotOnL1End(self, discontinuities):
        self.offsetsHandler.addDiscontinuities(self.reader.name, discontinuities)
        self.timeSeriesWidget.sig_files_plotted.emit()

    def slotOnBatchClicked(self, task, params):
        if len(self.fileDock.files) == 0:
            return
        if task == 'l1':
            self.batchWidget = L1BatchWidget(self.fileDock.files, self.offsetsHandler, params)
        elif task == 'fit':
            self.batchWidget = FitBatchWidget(self.fileDock.files, self.offsetsHandler, params)
        else:
            return
        self.batchWidget.show()
