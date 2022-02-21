from . qt import QtWidgets,QtCore,QtGui

from . import model


class QtIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, model):
        super(QtIconDelegate,self).__init__(model)

    def paint(self, painter, option, index):
        rect = option.rect.adjusted(1, 1, 0, 0)

        painter.fillRect(rect, option.palette.alternateBase())

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(rect, option.palette.base())

        painter.save()

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setOpacity(0.6)
            painter.fillRect(rect, option.palette.light())

        icon = index.data(model.Object)

        pixmap = icon.map
        if pixmap:
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.setOpacity(0.8)
            else:
                painter.setOpacity(1)
            painter.drawImage(
                rect.x()+(rect.width()-pixmap.width())/2,
                rect.y()+(rect.height()-pixmap.height())/2,pixmap
            )

        painter.restore()


class AtlasIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, model):
        super(AtlasIconDelegate,self).__init__(model)
        self.model = model

    def paint(self, painter, option, index):
        icon = index.data(model.Object)
        icon_size = icon.map.size()
        grid_h = icon_size.height()
        rect = option.rect

        painter.fillRect(rect, QtGui.QColor("#444444"))

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, QtGui.QColor("#555555"))

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(rect, option.palette.base())

        painter.save()


        name_rect = QtCore.QRectF(rect)
        name_rect.setWidth(icon.name_width)
        name_font = QtGui.QFont()
        name_metrics = QtGui.QFontMetrics(name_font)
        name_rect.translate(5, 5)

        name = icon.name.lower()
        # elide
        name = name_metrics.elidedText(
            name, QtCore.Qt.ElideRight, name_rect.width())

        # draw label
        if option.state & QtWidgets.QStyle.State_MouseOver or option.state & QtWidgets.QStyle.State_Selected:
            pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1)
        else:
            pen = QtGui.QPen(QtGui.QColor("#AAAAAA"), 1)
        painter.setPen(pen)
        painter.setFont(name_font)
        painter.drawText(name_rect, name)

        pixmap = icon.map
        icon_rect = option.rect.adjusted(icon.name_width, 0, 0, 0)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setOpacity(0.6)

        elif option.state & QtWidgets.QStyle.State_Selected:
            painter.setOpacity(0.9)

        painter.drawImage(icon_rect.x(), icon_rect.y(), pixmap)

        pen = QtGui.QPen(QtGui.QColor("#383838"), 1)
        painter.setPen(pen)
        for i in range(int(icon_rect.width()/grid_h)):
            grid_x = rect.x() + i*grid_h + icon.name_width
            painter.drawLine(
                grid_x,
                icon_rect.y(),
                grid_x,
                icon_rect.y()+grid_h
            )

        if not icon.selected == None and option.state & QtWidgets.QStyle.State_Selected:
            pen = QtGui.QPen(QtGui.QColor("#00FF00"), 1)
            painter.setPen(pen)
            grid_rect = QtCore.QRect(
                rect.x() + icon.name_width + icon.selected*grid_h, rect.y(), grid_h, grid_h)
            grid_rect = grid_rect.adjusted(1, 1, -1, -1)
            painter.drawRect(grid_rect)

        pen = QtGui.QPen(QtGui.QColor("#383838"), 1)
        painter.setPen(pen)
        painter.drawRect(rect)

        painter.restore()

    def sizeHint(self, option, index):
        icon = index.data(model.Object)
        return icon.map.size()

