import math
import threading

from .qt import QtCore

from pymxs import runtime as mxs


def get_max_version(year=True):
    v = mxs.maxversion()[0]
    return int(2000 + (math.ceil(v/1000.0)-2)) if year else v

def get_max_dir(name):
    return mxs.getdir(mxs.name(name))

def get_max_main_window():
    version = get_max_version()
    if version > 2020:
        import shiboken2
        from PySide2 import QtWidgets
        widget = QtWidgets.QWidget.find(mxs.windows.getMAXHWND())
        return shiboken2.wrapInstance(shiboken2.getCppPointer(widget)[0], QtWidgets.QMainWindow)
    else:
        import MaxPlus
        if version > 2017:
            return MaxPlus.GetQMaxMainWindow()
        elif version == 2017:
            return MaxPlus.GetQMaxWindow()



def run_thread(func,args=None):
    if not args:
        args = list()
    th = threading.Thread(target=func, args=args)
    th.start()

def defer(delay, func):
    if delay > 0:
        return QtCore.QTimer.singleShot(delay, func)
    else:
        return func()
