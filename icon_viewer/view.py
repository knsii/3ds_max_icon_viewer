from .qt import QtCore, QtWidgets
from . import model

class QtIconView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(QtIconView, self).__init__(parent)


class AtlasIconView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(AtlasIconView, self).__init__(parent)
        self.setMouseTracking(True)
        self.need_update = False

    def mousePressEvent(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            pos = event.pos()
            index = self.indexAt(event.pos())
            icon = index.data(model.Object)
            if not icon:
                return super(AtlasIconView, self).mousePressEvent(event)
            if event.button() == QtCore.Qt.LeftButton:
                item_height = icon.map.size().height()

                i_pos = pos.x()+self.horizontalScrollBar().sliderPosition()-icon.name_width
                icon.selected = None
                if i_pos > 0:
                    i = int(i_pos/item_height)
                    if i >= 0:
                        if self.need_update:
                            self.reset()
                            icon.selected = i
                            self.repaint()
                        else:
                            icon.selected = i
                            self.need_update = True
        return super(AtlasIconView, self).mousePressEvent(event)
