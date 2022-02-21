try:
    from PySide2 import QtWidgets, QtCore, QtGui
except:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

__qtbind__ = QtCore.__name__.split(".")[0]

if __qtbind__ == "PySide2":
    QSortFilterProxyModel = QtCore.QSortFilterProxyModel
    QStringListModel = QtCore.QStringListModel if hasattr(QtCore,"QStringListModel") else QtGui.QStringListModel
else:
    QSortFilterProxyModel = QtGui.QSortFilterProxyModel
    QStringListModel = QtGui.QStringListModel

