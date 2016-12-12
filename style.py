style = '''
QScrollBar:vertical {
     border: 1px solid rgb(200, 200, 200);
     background: rgb(251, 251, 251);
     width: 15px;
     margin: 22px 0 22px 0;
 }
 QScrollBar::handle:vertical {
     background-color: rgb(226, 226, 226);
     min-height: 20px;
 }
 QScrollBar::add-line:vertical {
     border: 1px solid rgb(200, 200, 200);
     background: rgb(226, 226, 226);
     height: 20px;
     subcontrol-position: bottom;
     subcontrol-origin: margin;
 }

 QScrollBar::sub-line:vertical {
     border: 1px solid rgb(200, 200, 200);
     background: rgb(226, 226, 226);
     height: 20px;
     subcontrol-position: top;
     subcontrol-origin: margin;
 }
 QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
     border: 1px solid rgb(200, 200, 200);
     width: 3px;
     height: 3px;
     background-color: rgb(226, 226, 226);
 }

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
     background: none;
 }

QMainWidnow, QWidget, QDockWidget,QCheckBox, QPushButton, QToolBox, QMenuBar {
    font: 10pt "Microsoft YaHei";
}

QListWidget {
    border: 1px solid rgb(200, 200, 200);
}

QMenuBar {
    background-color: rgb(251, 251, 251);
    border-bottom: 1px solid rgb(200, 200, 200);
}

QMenu::item {
    padding: 5px 20px;
    background-color: rgb(251, 251, 251);
}

QMenu::separator {
    height: 1px;
    background: rgb(200, 200, 200);
}

QMenu::item:selected {
    background-color: rgb(226, 226, 226);;
}

QMenu::indicator {
    width: 13px;
    height: 13px;
}

QMenu::item:hover, QPushButton::hover, QListView::item:hover {
    background-color:rgb(200, 200, 200);
}

QMenu::indicator:checked {
    background-image: url(:/resource/check.png);
}

QMenuBar::item {
    spacing: 3px;
    padding: 4px 8px;
    background: transparent;
}

QMenuBar::item:selected
{
    background-color: rgb(226, 226, 226);
    border: none;
}

QMenuBar::item:pressed {
    background-color: rgb(226, 226, 226);
    border: none;
}

QToolBar {
    spacing: 3px; /* spacing between items in the tool bar */
    background-color: rgb(251, 251, 251);
}
QToolBar::handle {
    background-color: rgba(0, 0, 0, 0);
}
QToolButton
{
    border: none;
}
QToolButton:hover
{
    background-color: rgb(226, 226, 226);
    border: none;
}
QToolButton:checked
{
    background-color: rgb(226, 226, 226);
    border: none;
}

QTabWidget::pane
{
    border: 1px solid rgb(200, 200, 200);
}

QTabBar::tab, QToolBox::tab {
    background-color: rgb(251, 251, 251);
    border: 1px solid rgb(200, 200, 200);
    padding: 3px 6px;
    border-bottom-color: none;
}

QTabBar::tab:selected, QTabBar::tab:hover, QToolBox::tab:selected, QToolBox::tab:hover {
    background-color: rgb(226, 226, 226);
}

QTabBar::tab:selected, QToolBox::tab:selected {
    border: 1px solid rgb(200, 200, 200);
    border-bottom-color: none;
     /* same as pane color */
}

QPushButton {
    background-color: rgb(226, 226, 226);
    border: 1px solid rgb(200, 200, 200);
    padding: 4px 8px;
}

QPushButton::pressed, QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background-color: rgb(180, 180, 180)
}


QLineEdit, QSpinBox {
    border: 1px solid rgb(200, 200, 200)
}

QLineEdit:read-only {
    background-color: rgb(226, 226, 226);
}

QComboBox {
    background-color: rgb(226, 226, 226);
    border: 1px solid rgb(200, 200, 200);
    padding: 3px 6px;
}

QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 13px;
    height: 13px;
}

QCheckBox::indicator:unchecked {
    image: url(:/resource/checkbox_unchecked.png);
}

QCheckBox::indicator:checked {
    image: url(:/resource/checkbox_checked.png);
}

QCheckBox::indicator:unchecked:hover {
    image: url(:/resource/checkbox_unchecked_hover.png);
}

QListView::item:selected {
    background-color: rgb(200, 200, 200);
    color: black;
}
'''

font_style = '''
QMainWidnow, QWidget, QDockWidget, QCheckBox, QPushButton, QToolBox, QMenuBar {
    font: 10pt "Microsoft YaHei";
}
QTabWidget::pane
{
    border: 1px solid rgb(200, 200, 200);
}

QTabBar::tab, QToolBox::tab {
    background-color: rgb(251, 251, 251);
    border: 1px solid rgb(200, 200, 200);
    padding: 3px 6px;
}

QTabBar::tab:selected, QTabBar::tab:hover, QToolBox::tab:selected, QToolBox::tab:hover {
    background-color: rgb(226, 226, 226);
}

QTabBar::tab:selected, QToolBox::tab:selected {
    border: 1px solid rgb(200, 200, 200);
}

QTabBar::tab, QTabBar::tab:selected {
    border-bottom-color: none;
}

QDockWidget {
    font-size: 12pt;
}

QGroupBox {
    border: 1px solid rgb(200, 200, 200);
    margin-top: 18px;
}

QGroupBox:title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding-right: 20000px;
    padding-top: 3px;
    padding-bottom: 3px;
    padding-left: 3px;
    background-color: rgb(226, 226, 226);
    border-bottom: 1px solid rgb(200, 200, 200);
}

'''
