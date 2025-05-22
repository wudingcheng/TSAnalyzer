#!/usr/bin/env python
# -*- coding: utf-8 -*-
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction
from qtpy.QtCore import Signal, Qt, QThread, QCoreApplication
# import matplotlib.dates as mdates # TODO: Refactor for pyqtgraph
from datetime import datetime
# from matplotlib.axes import Axes # TODO: Refactor for pyqtgraph
import pyqtgraph as pg
from collections import OrderedDict
# from .figure import MplCanvas # Removed MplCanvas
from ..models.offsets import DiscontinuityEvent, DISCONTINUITIES
from ..utils import makeAction
from ..thread.plot_thread import TimeSeriesThread

def _(text, disambiguation=None, context='TimeSeriesWidget'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)



class TimeSeriesWidget(QWidget):
    sig_message_update = Signal(str)
    # sig_discontinuity_added = Signal(datetime, Axes) # TODO: Refactor for pyqtgraph (Axes type)
    sig_discontinuity_added = Signal(datetime, object) # TODO: Refactor for pyqtgraph (Axes type)
    sig_discontinuity_removed = Signal(DiscontinuityEvent)
    sig_discontinuity_moved = Signal(DiscontinuityEvent)
    sig_discontinuity_hovered = Signal(DiscontinuityEvent)
    sig_discontinuity_visibled = Signal()
    sig_files_plotted = Signal()

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(TimeSeriesWidget, self).__init__(parent=parent)
        self.pgCanvas = pg.GraphicsLayoutWidget()
        vb = QVBoxLayout(self)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)
        vb.addWidget(self.pgCanvas)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.cursor_enabled = False
        self.plotItems = [] 
        self.discontinuityLines = {} # Store as {plot_item_object: [line_object, ...]}
        self._discontinuityDragged = None 
        self.active_plot_item = None # Keep track of plot item under mouse
        self.current_discontinuity_type = None # For toolbar interaction

        self.componentsAxes = {} 

        self.thread = TimeSeriesThread(self.pgCanvas) 
        self.thread.sig_time_series_end.connect(self.slotOnTimeSeriesPlotEnd)
        
        self.pgCanvas.scene().sigMouseMoved.connect(self.slotMouseMoved)
        self.pgCanvas.scene().sigMouseClicked.connect(self.slotMouseClickEvent)
        self.pgCanvas.scene().sigMouseReleased.connect(self.slotOnButtonRelease) # Connect mouse release

        self.menu = QMenu()
        self.__initActions()

    def __initActions(self):
        _actions = [
            # Removed "Resize figure" as pyqtgraph handles auto-resizing well.
            None,
            (self, _("Grid lines"), _("Grid"), self.slotOnFigureGrid, 'figure.grid', None, True),
            (self, _("Show discontinuities"), _("Discontinuities"),
             self.slotOnVisibleDiscontinuities, 'figure.discontinuity', None, True)
        ]
        self.actions = OrderedDict()
        for act in _actions:
            if act is not None:
                callback = act[3]
                action_key = act[4]
                is_toggle = act[6] if len(act) > 6 else False
                a = QAction(act[1], self, triggered=callback, checkable=is_toggle)
                a.setStatusTip(act[2])
                # Set initial checked state
                if action_key == 'figure.grid': a.setChecked(True) 
                if action_key == 'figure.discontinuity': a.setChecked(True)
                self.actions[action_key] = a
                self.menu.addAction(a)
            else:
                self.menu.addSeparator()
        
        # Apply initial state after actions are created
        if 'figure.grid' in self.actions:
             self.slotOnFigureGrid(self.actions['figure.grid'].isChecked())
        if 'figure.discontinuity' in self.actions:
             self.slotOnVisibleDiscontinuities(self.actions['figure.discontinuity'].isChecked())


    def slotOnFigureGrid(self, flag):
        for plot_item in self.plotItems:
            plot_item.showGrid(x=flag, y=flag, alpha=0.3 if flag else 0)

    def slotOnVisibleDiscontinuities(self, flag):
        for plot_item_lines_list in self.discontinuityLines.values():
            for line in plot_item_lines_list: # Iterate through the list of lines for that plot_item
                line.setVisible(flag)
                if hasattr(line, 'label') and line.label: # Also toggle label visibility
                    line.label.setVisible(flag)
        if flag: # This signal might be for external components to know visibility changed
            self.sig_discontinuity_visibled.emit()

    def setDiscontinuitiesVisible(self, text):
        # This method is called from discontinuity dock, potentially to filter specific types
        if text == "All":
            if 'figure.discontinuity' in self.actions:
                 self.actions['figure.discontinuity'].setChecked(True) # Sync action state
            self.slotOnVisibleDiscontinuities(True)
        else:
            # TODO: Implement filtering based on 'text' (Discontinuity type)
            # This would require storing the DiscontinuityEvent type with the line/label
            # and then iterating to show/hide matching types.
            if 'figure.discontinuity' in self.actions:
                 self.actions['figure.discontinuity'].setChecked(False) # Sync action state
            # As a placeholder, if not "All", hide all until filtering is implemented.
            # self.slotOnVisibleDiscontinuities(False)
            print(f"Filtering for discontinuity type '{text}' not yet fully implemented.")
        pass

    # def __initCursor(self): # Cursors (like crosshairs) are often added directly to PlotItems in pyqtgraph
    #     pass

    def slotOnDataLoaded(self, reader):
        # Clear previous plots and data before loading new ones
        for plot_item_key in list(self.discontinuityLines.keys()): # Iterate over a copy of keys
            for line in self.discontinuityLines[plot_item_key]:
                if hasattr(line, 'label') and line.label:
                    plot_item_key.removeItem(line.label) # Remove label from plot item
                plot_item_key.removeItem(line) # Remove line from plot item
        self.discontinuityLines.clear()
        
        for item in self.plotItems: # self.plotItems should hold PlotItem objects
            self.pgCanvas.removeItem(item) # Removes PlotItem from GraphicsLayout
        self.plotItems.clear()
        
        self.columns = reader.columns
        self.thread.render(reader, task='ts') 
        self.thread.start() 

    def slotOnTimeSeriesPlotEnd(self):
        self.plotItems = list(self.thread.plots) # Get PlotItems created by the thread
        self.componentsAxes = {pi.getAxis('left').labelText: pi for pi in self.plotItems if pi.getAxis('left').labelText}
        
        # After plots are created, apply initial grid/discontinuity visibility from menu actions
        if 'figure.grid' in self.actions:
            self.slotOnFigureGrid(self.actions['figure.grid'].isChecked())
        if 'figure.discontinuity' in self.actions:
            self.slotOnVisibleDiscontinuities(self.actions['figure.discontinuity'].isChecked())
            
        self.sig_files_plotted.emit()

    def slotOnFitOrResiduals(self, df, columns, task):
        # Similar to slotOnDataLoaded, clear old state before plotting new
        for plot_item_key in list(self.discontinuityLines.keys()):
            for line in self.discontinuityLines[plot_item_key]:
                if hasattr(line, 'label') and line.label:
                    plot_item_key.removeItem(line.label)
                plot_item_key.removeItem(line)
        self.discontinuityLines.clear()

        # PlotItems are recreated by the thread in fit/residuals mode currently
        for item in self.plotItems:
            self.pgCanvas.removeItem(item)
        self.plotItems.clear()

        self.thread.renderFitOrResiduals(df, columns, task)
        self.thread.start()

    def slotMouseMoved(self, pos): # 'pos' is the scene position from sigMouseMoved
        if not self.plotItems:
            self.active_plot_item = None
            self.sig_message_update.emit("") # Clear message if no plots
            return

        current_pi = None
        # Determine which PlotItem the mouse is over
        for plot_item in self.plotItems:
            if plot_item.sceneBoundingRect().contains(pos):
                current_pi = plot_item
                break
        
        self.active_plot_item = current_pi # Store the plot item under the mouse
        
        if self.active_plot_item:
            mouse_point = self.active_plot_item.vb.mapSceneToView(pos) # Map scene pos to view pos for this plot item
            x_timestamp = mouse_point.x()
            y_val = mouse_point.y()
            
            try:
                x_datetime = datetime.fromtimestamp(x_timestamp)
                date_str = x_datetime.strftime('%Y-%m-%d %H:%M:%S')
            except (TypeError, ValueError): # Handle potential errors if timestamp is out of range
                date_str = "N/A"

            component_name = self.active_plot_item.getAxis('left').labelText or "Y" # Default to "Y" if no label
            self.sig_message_update.emit(f"date={date_str} | {component_name}={y_val:.2f}")

            if self._discontinuityDragged: # If a line is being dragged
                # The line's position is relative to its parent PlotItem's ViewBox.
                # So, x_timestamp (which is already in the view's coordinates) is correct.
                self._discontinuityDragged.setValue(x_timestamp) 
                # Annotation update is handled by the line's sigPositionChanged -> handleDiscontinuityLineMoved
        else:
            self.sig_message_update.emit("") # Clear message if not over any plot item

    # Placeholder for other original event handlers that need refactoring or removal
    # def _setAxesCursorVisible(self, ax): pass
    # def slotCursorMoved(self, evt): pass # Replaced by logic in slotMouseMoved
    # def updateOffsetAnnotation(self, line): pass # Will be handled by InfLineLabel or similar
    # def setCursorsColor(self, color): pass
    # def slotEnterFigureEvent(self, evt): pass
    # def slotLeaveFigureEvent(self, evt): pass
    # def slotEnterAxesEvent(self, evt): pass
    # def slotLeaveAxesEvent(self, evt): pass
    # def setLabelAndCursorVisible(self, flag): pass
    # def slotOnPickEvent(self, event): pass # Replaced by line.sigClicked
    # def slotOnDiscontinuityPick(self, event): pass # Replaced by handleDiscontinuityLineClick
    # def slotOffsetMoved(self, evt): pass # Replaced by direct update in slotMouseMoved when dragging

    def slotMouseClickEvent(self, event): # event is GraphicsScene.MouseClickEvent
        if not self.cursor_enabled or not self.active_plot_item : 
            return

        # Check if click was on an existing InfiniteLine. The line's own sigClicked handles interaction.
        # We need to ensure this click doesn't simultaneously add a new point if it was on a line.
        items_under_cursor = self.pgCanvas.scene().items(event.scenePos())
        for item in items_under_cursor:
            if isinstance(item, pg.InfiniteLine):
                # Check if this line is one of ours
                for lines_in_plot in self.discontinuityLines.values():
                    if item in lines_in_plot:
                        # If an InfiniteLine is clicked, its own handler (handleDiscontinuityLineClick)
                        # will be invoked due to line.sigClicked.connect.
                        # We should not proceed to add a new discontinuity here.
                        return 
        
        if event.button() == Qt.LeftButton and self.active_plot_item:
            mouse_point = self.active_plot_item.vb.mapSceneToView(event.scenePos())
            x_timestamp = mouse_point.x()
            try:
                date_object = datetime.fromtimestamp(x_timestamp)
                # Create DiscontinuityEvent (model object)
                # Type could be set by a toolbar later, default for now.
                new_disc_event = DiscontinuityEvent(date=date_object, type='manual_offset') 
                
                self.sig_discontinuity_added.emit(date_object, self.active_plot_item) # Inform main application
                self.add_visual_discontinuity(new_disc_event, self.active_plot_item) # Add to plot
            except (TypeError, ValueError) as e:
                print(f"Error creating discontinuity: Invalid timestamp {x_timestamp}. {e}")

    def add_visual_discontinuity(self, disc_event, plot_item, movable=True):
        """Adds a visual pg.InfiniteLine to the specified plot_item, linked to a DiscontinuityEvent."""
        if not plot_item: return

        timestamp = disc_event.date.timestamp()
        # TODO: Customize pen based on disc_event.type using DISCONTINUITIES model mapping
        line_pen_color = 'r' # Default color
        # Example: if disc_event.type in DISCONTINUITIES: line_pen_color = DISCONTINUITIES[disc_event.type].color
        line_pen = pg.mkPen(line_pen_color, width=1.5)
        
        line = pg.InfiniteLine(pos=timestamp, angle=90, movable=movable, pen=line_pen)
        line.setHoverPen(pg.mkPen('g', width=2.5)) # Green hover pen
        
        # Store the model event object with the visual line
        line.discontinuity_event_ref = disc_event 

        # Create and add a label for the line
        label_text = f"{disc_event.type}: {disc_event.date.strftime('%Y-%m-%d')}"
        # InfLineLabel is associated with an InfiniteLine and moves with it.
        line_label = pg.InfLineLabel(line, text=label_text, position=0.95, anchor=(0.5, 0.5), color='k')
        line.label = line_label # Store for easy access/update

        plot_item.addItem(line) # Add line to the plot
        # plot_item.addItem(line_label) # InfLineLabel is often added automatically with its line or handled by it.
                                     # If not, it needs to be added to the same PlotItem or ViewBox.
                                     # pg.InfLineLabel is a GraphicsObject, it should be added to the plot.
                                     # However, its constructor links it to the line, so it might manage its own adding/removing with the line.
                                     # For safety, let's ensure it's added if it's a separate item.
                                     # After checking docs, InfLineLabel is a GraphicsObject, but it's typical to add it to the same viewbox/plotitem as the line.
                                     # The line itself is added to plot_item.vb (ViewBox), InfLineLabel also typically to vb.

        # Store the line, associated with its plot_item
        if plot_item not in self.discontinuityLines:
            self.discontinuityLines[plot_item] = []
        self.discontinuityLines[plot_item].append(line)

        # Connect signals for this specific line
        line.sigClicked.connect(self.handleDiscontinuityLineClick) # Pass (line, QMouseEvent)
        line.sigPositionChanged.connect(self.handleDiscontinuityLineMoved) # Pass (line)
        line.sigDragFinished.connect(self.handleDiscontinuityLineDragFinished) # Pass (line)
        # line.sigHoverEvent.connect(self.handleDiscontinuityLineHover) # TODO: Implement hover effects if needed

    def handleDiscontinuityLineClick(self, line, event): # event is QMouseEvent from InfiniteLine's sigClicked
        """Handles clicks on an InfiniteLine representing a discontinuity."""
        event.accept() # Consume the event to prevent further processing by parent items
        
        # Find which plot_item this line belongs to
        active_plot_for_line = None
        for pi, lines_in_pi in self.discontinuityLines.items():
            if line in lines_in_pi:
                active_plot_for_line = pi
                break
        if not active_plot_for_line: return # Should not happen if line is in self.discontinuityLines

        if event.button() == Qt.RightButton:
            if line in self.discontinuityLines.get(active_plot_for_line, []):
                self.discontinuityLines[active_plot_for_line].remove(line)
                if hasattr(line, 'label') and line.label: 
                    active_plot_for_line.removeItem(line.label) # Remove label explicitly
                active_plot_for_line.removeItem(line) # Remove line
                if line.discontinuity_event_ref:
                     self.sig_discontinuity_removed.emit(line.discontinuity_event_ref) # Emit model event
            if self._discontinuityDragged == line: # If it was being dragged, clear it
                self._discontinuityDragged = None
        elif event.button() == Qt.MiddleButton: 
             self._discontinuityDragged = line
             line.setPen(pg.mkPen('b', width=3)) # Visual cue: blue, thicker pen for dragging
        elif event.button() == Qt.LeftButton:
            # Left click on a line could select it or show detailed info.
            if line.discontinuity_event_ref:
                 self.sig_discontinuity_hovered.emit(line.discontinuity_event_ref) # Re-use hover for "selection"
            
            # Visual cue for selection: make selected line yellow, others default
            for pi_lines_list in self.discontinuityLines.values():
                for other_line in pi_lines_list:
                    if other_line == line:
                        other_line.setPen(pg.mkPen('y', width=2.5)) # Selected line pen
                    else:
                        # TODO: Reset to original pen based on type, not just 'r'
                        other_line.setPen(pg.mkPen('r', width=1.5)) # Default pen for non-selected

    def handleDiscontinuityLineMoved(self, line): # Emitted when line.setValue() is called or dragged
        """Handles when a movable InfiniteLine's position is changed."""
        if line.discontinuity_event_ref: # Check if the event reference exists
            new_timestamp = line.value()
            try:
                new_date = datetime.fromtimestamp(new_timestamp)
                line.discontinuity_event_ref.date = new_date # Update the model object
                # Update the label text
                if hasattr(line, 'label') and line.label: 
                    new_label_text = f"{line.discontinuity_event_ref.type}: {new_date.strftime('%Y-%m-%d')}"
                    line.label.setText(new_label_text)
                self.sig_discontinuity_moved.emit(line.discontinuity_event_ref) # Emit model event
            except (TypeError, ValueError):
                pass # Invalid timestamp during drag, ignore for now

    def handleDiscontinuityLineDragFinished(self, line):
        """Handles when dragging of an InfiniteLine is finished."""
        if self._discontinuityDragged == line:
            # Reset pen to default or selected state
            # Check if it's the "selected" line (yellow pen)
            current_pen = line.pen
            selected_pen_color = pg.mkPen('y', width=2.5).color()
            if not (current_pen.color() == selected_pen_color and current_pen.width() == 2.5) :
                 # TODO: Reset to original pen based on type, not just 'r'
                line.setPen(pg.mkPen('r', width=1.5)) # Reset to default if not the selected line
            self._discontinuityDragged = None
            # Final update of annotation/model can be done here if sigPositionChanged is too frequent
            # self.updateOffsetAnnotation(line) # Or ensure label is correctly updated

    # def handleDiscontinuityLineHover(self, line, event): # TODO: Implement if specific hover effects are needed
    #     if event.isEnter():
    #         # Example: line.setPen(custom_hover_pen)
    #         if line.discontinuity_event_ref:
    #             self.sig_discontinuity_hovered.emit(line.discontinuity_event_ref) # If hover should also emit this
    #     elif event.isExit():
    #         # Example: line.setPen(original_pen_based_on_type_or_selection_state)
    #         pass

    def slotOnButtonRelease(self, event): # event is GraphicsScene.MouseClickEvent (despite name)
        if self._discontinuityDragged and event.button() == Qt.MiddleButton: # If drag was initiated by middle button
            # Call drag finished handler explicitly, as sigDragFinished might not cover all edge cases or specific button releases.
            self.handleDiscontinuityLineDragFinished(self._discontinuityDragged)

    def contextMenuEvent(self, event):
        # Show context menu only if there are plots and cursor is not enabled (i.e., not in discontinuity adding mode)
        if self.plotItems and not self.cursor_enabled:
            self.menu.exec_(self.mapToGlobal(event.pos()))

