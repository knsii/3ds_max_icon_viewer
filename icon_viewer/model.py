from .qt import QtCore

Object = QtCore.Qt.UserRole + 1
IconName = QtCore.Qt.UserRole + 2


class QtIconModel(QtCore.QAbstractListModel):
    def __init__(self, icons=None):
        super(QtIconModel, self).__init__()
        self.icons = icons if icons else []

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.icons)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            icon = self.icons[index.row()]
            if role == Object:
                return icon
            if role == IconName:
                return icon.name
            if role == QtCore.Qt.ToolTipRole:
                icon_count =len(icon.icons)
                sizes_tip = "<br><font color='#FFB100'>" + str(icon_count)+" size"+("s" if icon_count > 1 else "")+"</font>"
                return icon.name + sizes_tip

    def append(self,icon):
        self.beginInsertRows(QtCore.QModelIndex(),self.rowCount(),self.rowCount())
        self.icons.append(icon)
        self.endInsertRows()


class AtlasIconModel(QtCore.QAbstractListModel):
    def __init__(self, icons=None):
        super(AtlasIconModel, self).__init__()
        self.icons = icons if icons else []

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.icons)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            icon = self.icons[row]
            if role == Object:
                return icon
            if role == IconName:
                return icon.name
        else:
            return None

    def append(self,icon):
        self.beginInsertRows(QtCore.QModelIndex(),self.rowCount(),self.rowCount())
        self.icons.append(icon)
        self.endInsertRows()