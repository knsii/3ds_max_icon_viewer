# Qt compatibility layer.
# 3ds Max 2025+ ships PySide6 (Qt 6). Max 2019-2024 ship PySide2 (Qt 5).
# Every other file imports Qt from here, so only this file needs to know which one is present.
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    import shiboken6 as shiboken
    QAction = QtGui.QAction            # QAction moved from QtWidgets to QtGui in Qt 6
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    import shiboken2 as shiboken
    QAction = QtWidgets.QAction

__qtbind__ = QtCore.__name__.split(".")[0]

QSortFilterProxyModel = QtCore.QSortFilterProxyModel
QStringListModel = QtCore.QStringListModel


def set_filter_text(proxy, text):
    """Filter a proxy model by search text (case insensitive).
    Qt 6 removed setFilterRegExp, so use QRegularExpression when available."""
    if __qtbind__ == "PySide6":
        rx = QtCore.QRegularExpression(
            text, QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption)
        proxy.setFilterRegularExpression(rx)
    else:
        proxy.setFilterRegExp(text)
