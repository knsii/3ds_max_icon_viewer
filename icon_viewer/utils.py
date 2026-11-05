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
        # qtmax is Autodesk's helper module (Max 2021+); works with PySide2 and PySide6
        try:
            import qtmax
            return qtmax.GetQMaxMainWindow()
        except ImportError:
            from .qt import QtWidgets, shiboken
            widget = QtWidgets.QWidget.find(mxs.windows.getMAXHWND())
            return shiboken.wrapInstance(shiboken.getCppPointer(widget)[0], QtWidgets.QMainWindow)
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
