#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from qtpy.QtWidgets import QToolBar, QAction, QFileDialog, QStyle, QActionGroup
from qtpy.QtCore import Signal, Qt, QCoreApplication
# Removed: from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# Removed: import matplotlib

from ..models.offsets import DISCONTINUITIES # DiscontinuityEvent not needed here
from ..utils import makeAction # Keep makeAction if it's generic for QAction creation
from pyqtgraph.exporters import ImageExporter # For saving


def _(text, disambiguation=None, context='TimeSeriesToolBar'):
    """Translate text."""
    return QCoreApplication.translate(context, text, disambiguation)


class TimeSeriesToolBar(QToolBar):
    sig_discontinuity_triggered = Signal(str, bool) # Keep this signal
    # _actionValidation not directly needed in the same way; will manage exclusivity with QActionGroup

    def __init__(self, timeseries_widget, parent=None): # Changed signature
        super(TimeSeriesToolBar, self).__init__(parent)
        self.timeseries_widget = timeseries_widget
        self.setWindowTitle("Time Series ToolBar")
        self._active_discontinuity_action = None # To track the currently active discontinuity QAction
        
        self._actions = {} # Store actions for potential external access or state update
        
        # Action group for discontinuity types (exclusive)
        self._discontinuity_action_group = QActionGroup(self)
        self._discontinuity_action_group.setExclusive(True)

        # Action group for mouse modes like Pan/Zoom (exclusive)
        self._mouse_mode_action_group = QActionGroup(self)
        self._mouse_mode_action_group.setExclusive(True)

        self._populate_toolbar()

    def _getDiscontinuitiesActions(self):
        actions_tuples = []
        for key, item_model in DISCONTINUITIES.items(): # item is now item_model for clarity
            # makeAction args: (parent, text, tooltip, callback, icon_path, action_key, is_toggle)
            # The original makeAction might need adjustment if icon handling is very matplotlib specific.
            # Assuming item_model.getIcon() returns a path or QIcon compatible string.
            # The callback is self.slotOnDiscontinuityTriggered.
            # action_key is item_model.key.
            actions_tuples.append((
                self, # parent for makeAction
                _(item_model.getDescription()), # text for action
                _(item_model.getName()), # tooltip
                lambda checked, action_key=item_model.key: self.slotOnDiscontinuityTriggered(checked, action_key), # callback with action_key
                item_model.getIcon(), # icon path/name
                item_model.key, # action_key used internally by makeAction if any
                True) # is_toggle
            )
        return actions_tuples

    def _populate_toolbar(self):
        # Home Action
        home_action = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), _('Reset original view (Home)'), self)
        home_action.setStatusTip(_('Reset plot views to their original data range'))
        home_action.triggered.connect(self.home_view)
        self.addAction(home_action)
        self._actions['home'] = home_action

        # Back Action
        back_action = QAction(self.style().standardIcon(QStyle.SP_ArrowBack), _('Back to previous view'), self)
        back_action.setStatusTip(_('Restore previous zoom/pan state'))
        back_action.triggered.connect(self.back_view)
        self.addAction(back_action)
        self._actions['back'] = back_action

        # Forward Action
        forward_action = QAction(self.style().standardIcon(QStyle.SP_ArrowForward), _('Forward to next view'), self)
        forward_action.setStatusTip(_('Restore next zoom/pan state'))
        forward_action.triggered.connect(self.forward_view)
        self.addAction(forward_action)
        self._actions['forward'] = forward_action
        
        self.addSeparator()

        # Pan Mode Action
        # Using SP_Arrow मूव as a placeholder, better icon might be needed
        pan_action = QAction(self.style().standardIcon(QStyle.SP_ArrowMove), _('Pan mode (Right or Middle mouse button)'), self)
        pan_action.setToolTip(_('Activates Pan mode. Use Right or Middle mouse button to pan.'))
        pan_action.setCheckable(True)
        pan_action.triggered.connect(lambda checked: self.pan_mode(checked))
        self.addAction(pan_action)
        self._actions['pan'] = pan_action
        self._mouse_mode_action_group.addAction(pan_action)
        
        # Zoom Mode Action (Rectangle Zoom)
        # Using SP_FileDialogListView as a placeholder, better icon might be needed (e.g. a magnifying glass with a rectangle)
        zoom_action = QAction(self.style().standardIcon(QStyle.SP_FileDialogListView), _('Zoom to rectangle mode'), self)
        zoom_action.setToolTip(_('Activates Zoom to Rectangle mode. Use Left mouse button to draw a rectangle to zoom.'))
        zoom_action.setCheckable(True)
        zoom_action.triggered.connect(lambda checked: self.zoom_mode(checked))
        self.addAction(zoom_action)
        self._actions['zoom'] = zoom_action
        self._mouse_mode_action_group.addAction(zoom_action)
        
        # Set Pan as default checked mode
        pan_action.setChecked(True)
        self.pan_mode(True) # Apply the default mode effect

        self.addSeparator()
        
        # Save Figure Action
        save_action = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), _('Save the figure'), self)
        save_action.setStatusTip(_('Save the current figure to an image file'))
        save_action.triggered.connect(self.save_figure)
        self.addAction(save_action)
        self._actions['save'] = save_action
        
        self.addSeparator()

        # Discontinuity Actions
        discontinuity_actions_tuples = self._getDiscontinuitiesActions()
        for act_tuple in discontinuity_actions_tuples:
            # makeAction(parent, text, tooltip, callback, icon_path, action_key_for_dict, is_toggle)
            # The callback in act_tuple already includes the action_key via lambda.
            # The action_key_for_dict (act_tuple[5]) is for self._actions.
            
            # Simpler QAction creation if makeAction is problematic:
            action_text = act_tuple[1] 
            tooltip = act_tuple[2]
            callback = act_tuple[3] # This is the lambda
            icon_path_or_qicon = act_tuple[4] # Assuming this can be handled by QIcon
            action_key = act_tuple[5] # e.g., 'offset', 'postseismic'
            
            q_action = QAction(action_text, self) # TODO: Add icon via QIcon(icon_path_or_qicon)
            q_action.setToolTip(tooltip)
            q_action.setCheckable(True)
            q_action.setProperty("action_key", action_key) # Store key for the slot
            q_action.triggered.connect(callback) # Connect the lambda
            
            self.addAction(q_action)
            self._actions[action_key] = q_action
            self._discontinuity_action_group.addAction(q_action)


    def home_view(self):
        if self.timeseries_widget and self.timeseries_widget.plotItems:
            for plot_item in self.timeseries_widget.plotItems:
                plot_item.autoRange()

    def back_view(self):
        if self.timeseries_widget and self.timeseries_widget.plotItems:
            for plot_item in self.timeseries_widget.plotItems:
                try:
                    plot_item.getViewBox().viewHistoryBack()
                except IndexError: # No more history
                    pass # Or provide user feedback

    def forward_view(self):
        if self.timeseries_widget and self.timeseries_widget.plotItems:
            for plot_item in self.timeseries_widget.plotItems:
                try:
                    plot_item.getViewBox().viewHistoryNext()
                except IndexError: # No more history
                    pass # Or provide user feedback
    
    def pan_mode(self, checked):
        if checked:
            if self.timeseries_widget and self.timeseries_widget.plotItems:
                for plot_item in self.timeseries_widget.plotItems:
                    plot_item.getViewBox().setMouseMode(pg.ViewBox.PanMode)
                # When pan mode is activated, ensure discontinuity mode is off
                current_disc_action = self._discontinuity_action_group.checkedAction()
                if current_disc_action:
                    current_disc_action.setChecked(False) 
                    # This will trigger slotOnDiscontinuityTriggered(False, ...)
                self.timeseries_widget.cursor_enabled = False
                self.timeseries_widget.pgCanvas.setCursor(Qt.ArrowCursor)
        else: # Pan mode was unchecked
            # If no other mouse mode is now active (e.g. user unclicked Pan), default to PanMode
            if not self._mouse_mode_action_group.checkedAction() and self.timeseries_widget and self.timeseries_widget.plotItems:
                for plot_item in self.timeseries_widget.plotItems:
                    plot_item.getViewBox().setMouseMode(pg.ViewBox.PanMode) 


    def zoom_mode(self, checked):
        if checked:
            if self.timeseries_widget and self.timeseries_widget.plotItems:
                for plot_item in self.timeseries_widget.plotItems:
                    plot_item.getViewBox().setMouseMode(pg.ViewBox.RectMode)
                # When zoom mode is activated, ensure discontinuity mode is off
                current_disc_action = self._discontinuity_action_group.checkedAction()
                if current_disc_action:
                    current_disc_action.setChecked(False)
                self.timeseries_widget.cursor_enabled = False
                self.timeseries_widget.pgCanvas.setCursor(Qt.ArrowCursor) # Or a zoom cursor (e.g. Qt.CrossCursor)
        else: # Zoom mode was unchecked
            # If no other mouse mode is now active, default to PanMode
            if not self._mouse_mode_action_group.checkedAction() and self.timeseries_widget and self.timeseries_widget.plotItems:
                for plot_item in self.timeseries_widget.plotItems:
                    plot_item.getViewBox().setMouseMode(pg.ViewBox.PanMode)


    def save_figure(self):
        if not self.timeseries_widget or not self.timeseries_widget.pgCanvas:
            return
        
        fileName, _ = QFileDialog.getSaveFileName(self, _("Save Figure"), "", 
                                                  _("PNG Image (*.png);;JPEG Image (*.jpg);;SVG Image (*.svg);;All Files (*)"))
        if fileName:
            try:
                exporter = ImageExporter(self.timeseries_widget.pgCanvas.scene())
                exporter.export(fileName)
            except Exception as e:
                # TODO: Show error message to user via QMessageBox
                print(f"Error saving figure: {e}")

    def set_message(self, s): # Matplotlib compatibility, no longer used internally
        pass

    def slotOnDiscontinuityTriggered(self, flag, action_key): # action_key passed from lambda
        # action_key is like 'offset', 'postseismic', etc.
        
        if flag: # Action was toggled on
            self.timeseries_widget.current_discontinuity_type = action_key
            self.timeseries_widget.cursor_enabled = True
            self.timeseries_widget.pgCanvas.setCursor(Qt.CrossCursor)
            self._active_discontinuity_action = self.sender() 
            
            # Deactivate Pan/Zoom mode if a discontinuity action is selected
            current_mouse_mode_action = self._mouse_mode_action_group.checkedAction()
            if current_mouse_mode_action:
                current_mouse_mode_action.setChecked(False)
            # And ensure default mouse mode for plot items if needed when adding discontinuities
            for plot_item in self.timeseries_widget.plotItems:
                 # Set to PanMode to allow clicks to register for adding points, RectMode would capture clicks.
                 # Or set to a custom "None" mode if available, but PanMode is often fine.
                plot_item.getViewBox().setMouseMode(pg.ViewBox.PanMode) # Or a "do nothing" mode

        else: # Action was toggled off
            # This part is tricky with QActionGroup(exclusive=True).
            # An action is usually only 'flagged' false if it's clicked again to untoggle it,
            # OR if another action in an exclusive group forces it off (but then the new one is flagged true).
            # We only want to reset if NO discontinuity action is active.
            active_disc_action = self._discontinuity_action_group.checkedAction()
            if not active_disc_action: # No discontinuity action is currently checked
                self.timeseries_widget.current_discontinuity_type = None
                self.timeseries_widget.cursor_enabled = False
                self.timeseries_widget.pgCanvas.setCursor(Qt.ArrowCursor)
                self._active_discontinuity_action = None
                # Restore a default mouse mode (e.g., Pan) if no other mouse mode is active
                if not self._mouse_mode_action_group.checkedAction():
                    if 'pan' in self._actions: # Check if pan action exists
                        self._actions['pan'].setChecked(True) # Default to pan mode
                        # self.pan_mode(True) will be called by the setChecked signal if not already in pan mode


        # Emit signal for external components if needed
        self.sig_discontinuity_triggered.emit(action_key, flag)


    def _update_buttons_checked(self): # Replaced by QActionGroup for discontinuities
        # For Pan/Zoom modes, if implemented, a similar logic might be needed
        pass
