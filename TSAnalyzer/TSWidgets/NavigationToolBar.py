import os

import matplotlib
from matplotlib.backend_bases import NavigationToolbar2, cursors
from matplotlib.backends.backend_qt5 import SubplotToolQt

# from PyQt4 import QtCore
# from PyQt4.QtGui import QFileDialog, QIcon, QInputDialog, QMessageBox, QToolBar

from qtpy import QtCore
from qtpy.QtWidgets import QFileDialog, QMessageBox, QToolBar, QInputDialog
from qtpy.QtGui import QIcon
from qtpy.compat import getsavefilename

# import images
try:
    import matplotlib.backends.qt_editor.figureoptions as figureoptions
except ImportError:
    figureoptions = None


cursord = {
    cursors.MOVE: QtCore.Qt.SizeAllCursor,
    cursors.HAND: QtCore.Qt.PointingHandCursor,
    cursors.POINTER: QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION: QtCore.Qt.CrossCursor,
}


class NavigationToolbar(NavigationToolbar2, QToolBar):

    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        # ('Cursor', 'Display vertical line', '', 'cursor'),
        (None, None, None, None),
        ('Grid', 'Toogle grid', '', 'grid'),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )

    def __init__(self, canvas, parent, coordinates=True):
        """ coordinates: should we show the coordinates on the right? """
        self.canvas = canvas
        self.parent = parent
        self.coordinates = coordinates
        self._actions = {}

        self.cursor_line = None
        self.cursor_cid = None
        self.color = 'r'

        QToolBar.__init__(self, parent)
        NavigationToolbar2.__init__(self, canvas)

    def _icon(self, name):
        # print os.path.join(self.basedir, name)
        # return QIcon(os.path.join(self.basedir, name))
        return QIcon(self.basedir + name)

    def _init_toolbar(self):
        self.basedir = ':/TSResource/images/'
        for text, tooltip_text, _, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(text.lower() + '.png'),
                                   text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan', 'cursor', 'grid']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        if figureoptions is not None:
            a = self.addAction(self._icon("options.png"),
                               'Customize', self.edit_parameters)
            a.setToolTip('Edit curves line and axes parameters')

        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        # if self.coordinates:
        #     self.locLabel = QLabel("", self)
        #     self.locLabel.setAlignment(
        #         QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #     self.locLabel.setSizePolicy(
        #         QSizePolicy(QSizePolicy.Expanding,
        #                     QSizePolicy.Expanding))
        #     labelAction = self.addWidget(self.locLabel)
        #     labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None

    if figureoptions is not None:
        def edit_parameters(self):
            allaxes = self.canvas.figure.get_axes()
            if not allaxes:
                QMessageBox.warning(
                    self.parent, "Error", "There are no axes to edit.")
                return
            if len(allaxes) == 1:
                axes = allaxes[0]
            else:
                titles = []
                for axes in allaxes:
                    title = axes.get_title()
                    ylabel = axes.get_ylabel()
                    label = axes.get_label()
                    if title:
                        fmt = "%(title)s"
                        if ylabel:
                            fmt += ": %(ylabel)s"
                        fmt += " (%(axes_repr)s)"
                    elif ylabel:
                        fmt = "%(axes_repr)s (%(ylabel)s)"
                    elif label:
                        fmt = "%(axes_repr)s (%(label)s)"
                    else:
                        fmt = "%(axes_repr)s"
                    titles.append(fmt % dict(title=title,
                                             ylabel=ylabel, label=label,
                                             axes_repr=repr(axes)))
                item, ok = QInputDialog.getItem(
                    self.parent, 'Customize', 'Select axes:', titles, 0, False)
                if ok:
                    axes = allaxes[titles.index(six.text_type(item))]
                else:
                    return

            figureoptions.figure_edit(axes, self)

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['zoom'].setChecked(self._active == 'ZOOM')
        # self._actions['cursor'].setChecked(self._active == 'CURSOR')

    def grid(self):
        for ax in self.canvas.figure.get_axes():
            ax.grid(which="both")
        self.canvas.draw_idle()

    def cursor(self):
        if self._active == 'CURSOR':
            self._active = None
        else:
            self._active = 'CURSOR'

        if self.cursor_cid is not None:
            self.cursor_cid = self.canvas.mpl_disconnect(self.cursor_cid)

        if self._active:
            self.cursor_cid = self.canvas.mpl_connect('motion_notify_event',
                                                      self.cursor_motion)
            self.mode = 'cursor'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self._update_buttons_checked()

    def cursor_motion(self, event):
        ax = event.inaxes
        if ax not in self.canvas.figure.get_axes():
            if self.cursor_line:
                try:
                    self.cursor_line.remove()
                except:
                    pass
                self.cursor_line = None
        elif self.cursor_line is not None:
            if self.cursor_line.axes == ax:
                self.cursor_line.set_xdata(event.xdata)
            else:
                self.cursor_line.remove()
                self.cursor_line = None
                self.cursor_motion(event)
        else:
            self.cursor_line = ax.axvline(event.xdata, color=self.color)
        self.canvas.draw_idle()

    def pan(self, *args):
        super(NavigationToolbar, self).pan(*args)
        self._update_buttons_checked()

    def zoom(self, *args):
        super(NavigationToolbar, self).zoom(*args)
        self._update_buttons_checked()

    def dynamic_update(self):
        self.canvas.draw_idle()

    def set_message(self, s):
        if self.coordinates:
            try:
                self.nativeParentWidget().statusbar.showMessage(s)
            except:
                self.locLabel.setText(s)

    def set_cursor(self, cursor):
        self.canvas.setCursor(cursord[cursor])

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0

        w = abs(x1 - x0)
        h = abs(y1 - y0)

        rect = [int(val)for val in (min(x0, x1), min(y0, y1), w, h)]
        self.canvas.drawRectangle(rect)

    def remove_rubberband(self):
        self.canvas.drawRectangle(None)

    def configure_subplots(self):
        image = os.path.join(matplotlib.rcParams['datapath'],
                             'images', 'matplotlib.png')
        dia = SubplotToolQt(self.canvas.figure, self.parent)
        dia.setWindowIcon(QIcon(image))
        dia.exec_()

    def save_figure(self, *args):
        # filetypes = self.canvas.get_supported_filetypes_grouped()
        # sorted_filetypes = list(six.iteritems(filetypes))
        # sorted_filetypes.sort()
        # default_filetype = self.canvas.get_default_filetype()

        # startpath = matplotlib.rcParams.get('savefig.directory', '')
        # startpath = os.path.expanduser(startpath)
        # start = os.path.join(startpath, self.canvas.get_default_filename())
        # filters = []
        # selectedFilter = None
        # for name, exts in sorted_filetypes:
        #     exts_list = " ".join(['*.%s' % ext for ext in exts])
        #     filter = '%s (%s)' % (name, exts_list)
        #     if default_filetype in exts:
        #         selectedFilter = filter
        #     filters.append(filter)
        # filters = ';;'.join(filters)

        # fname, filter = _getSaveFileName(self.parent,
        #                                  "Choose a filename to save to",
        #                                  start, filters, selectedFilter)
        # if fname:
        #     if startpath == '':
        #         # explicitly missing key or empty str signals to use cwd
        #         matplotlib.rcParams['savefig.directory'] = startpath
        #     else:
        #         # save dir for next time
        #         savefig_dir = os.path.dirname(six.text_type(fname))
        #         matplotlib.rcParams['savefig.directory'] = savefig_dir
        #     try:
        #         self.canvas.print_figure(six.text_type(fname))
        #     except Exception as e:
        #         QMessageBox.critical(
        #             self, "Error saving file", six.text_type(e),
        #             QMessageBox.Ok, QMessageBox.NoButton)
        saved_filename = getsavefilename(
            self,
            'Save Images',
            'untitled.png',
            '(*.jpg *.pdf *.eps *.png)')[0]
        saved_filename = str(saved_filename)
        if saved_filename:
            self.canvas.figure.savefig(saved_filename, dpi=300)
