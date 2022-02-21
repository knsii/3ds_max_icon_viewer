import os
import sys
from collections import OrderedDict as odict

from .qt import QtWidgets,QtCore


from . widget import QtIconPage, AtlasIconPage, AboutPage
from . control import IconViewerController
from . import utils

self = sys.modules[__name__]
self._window = None


class MaxIconViewer(QtWidgets.QDialog):
    def __init__(self,control, parent=None):
        super(MaxIconViewer, self).__init__(parent)
        self.control = control

        control.was_qt_icon_loaded.connect(self.on_qt_icon_loaded)

        with open(os.path.join(os.path.dirname(__file__),"style.qss"),"r") as f:
            self.setStyleSheet(f.read())

        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        self.max_version = utils.get_max_version()
        self.setWindowTitle("icons in 3dsmax " + str(self.max_version))
        self.resize(695, 387)

        widgets = {
            "tab": QtWidgets.QTabWidget()
        }
        pages = odict((
            ("icons", QtIconPage(control)),
            ("old icons (bmp)", AtlasIconPage(control)),
            ("about", AboutPage(control)),
        ))

        widget = widgets["tab"]
        widget.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for name, page in pages.items():
            widget.addTab(page, name)

    def on_qt_icon_loaded(self,icons,tree):
        self.setWindowTitle(self.windowTitle() +  " (%s icons loaded)"%len(icons))

def show():
    ctrl = IconViewerController()
    if self._window:
        self._window.close()
    self._window = MaxIconViewer(ctrl,parent=utils.get_max_main_window())
    self._window.show()

if __name__ == "__main__":
    show()