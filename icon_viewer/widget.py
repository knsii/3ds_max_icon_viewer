import os
import re
import subprocess

from .qt import QtWidgets,QtCore,QtGui,QSortFilterProxyModel,QStringListModel, __qtbind__

from . import model, view, delegate, data



class Notification(QtWidgets.QLabel):
    def __init__(self, parent=None, message="", duration=1700, background="#CC383838", color="#ffffff"):
        super(Notification, self).__init__(parent)
        self.hide()
        self.setText(message)
        self.setMargin(10)
        self.setStyleSheet(
            '''QLabel {background-color:%s;border-radius: 2px;color:%s;}''' % (background, color))

        self.effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)

        self.anime = QtCore.QPropertyAnimation(self.effect, b"opacity")
        anime = self.anime
        anime.setDuration(duration)
        anime.setStartValue(1)
        anime.setEndValue(0)
        anime.setEasingCurve(QtCore.QEasingCurve.InQuad)
        anime.finished.connect(self.close)

    def show(self, message=None):
        if message:
            self.setText(message)
        self.anime.stop()
        self.hide()
        self.anime.start()
        self.adjustSize()
        self.update()
        center = self.parentWidget().size()
        self.move(center.width() * .5 - self.width() * .5,
                  center.height() * .5 - self.height())
        super(Notification, self).show()

    def mousePressEvent(self, event):
        self.close()


class IconPreviewer(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(IconPreviewer, self).__init__(parent)

        self.setStyleSheet("QDialog{background-color:#444444;border:1px solid #000000}")
        self.setWindowFlags(QtCore.Qt.Popup)
        layout = QtWidgets.QVBoxLayout(self)

        widgets = {
            "image": QtWidgets.QLabel(),
            "label": QtWidgets.QLabel()
        }

        widget = widgets["label"]
        widget.setAlignment(QtCore.Qt.AlignCenter)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                            QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(widget)

        widget = widgets["image"]
        widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(widget)

        self.widgets = widgets

    def show(self,icon_file):
        self.setWindowTitle(icon_file)
        pixmap = QtGui.QPixmap(icon_file)
        ori_size = pixmap.size()
        size = QtCore.QSize(min([pixmap.width(), 500]),
                            min([pixmap.height(), 500]))
        size = QtCore.QSize(max([size.width(), 64]),
                            max([size.height(), 64]))
        pixmap = pixmap.scaled(size.width(), size.height(),
                               QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation)
        widget = self.widgets["image"]
        widget.setPixmap(pixmap)
        widget.resize(size.width(), size.height())
        widget = self.widgets["label"]
        widget.setText("%s <font color='#777777'>x</font> %s px" % (ori_size.width(), ori_size.height()))

        super(IconPreviewer, self).show()




class IconCatTree(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(IconCatTree, self).__init__(parent)
        _model = QtGui.QStandardItemModel()
        self.setModel(_model)

    def set_data(self,data):
        def fill(parent, d):
            if isinstance(d, dict):
                for key, value in d.items():
                    it = QtGui.QStandardItem(str(key))
                    if isinstance(value, dict):
                        parent.appendRow(it)
                        fill(it, value)

        fill(self.model().invisibleRootItem(), data)
        self.model().setHorizontalHeaderLabels(['categories'])




class QtIconPage(QtWidgets.QWidget):
    def __init__(self,control, parent=None):
        super(QtIconPage, self).__init__(parent)

        self.control = control

        panels = {
            "icon_panel": QtWidgets.QSplitter(),
            "icon_info": QtWidgets.QGroupBox("details"),
            "list_panel": QtWidgets.QWidget(),
        }
        widgets = {
            "notification": Notification(),
            "icon_tree": IconCatTree(),

            "search": QtWidgets.QLineEdit(),
            "icon_list": view.QtIconView(),

            # icon detail
            "icon_count": QtWidgets.QLabel("0 size"),
            "icon_names": QtWidgets.QComboBox(),

            "progress":QtWidgets.QProgressBar(),
        }

        buttons = {
            "copy_text": QtWidgets.QToolButton(),
            "open_file": QtWidgets.QToolButton(),
            "save_file": QtWidgets.QToolButton(),
            "view_file": QtWidgets.QToolButton(),
        }

        models = {
            "icon": model.QtIconModel()
        }

        for name, widget in widgets.items():
            widget.setObjectName(name)

        for name, widget in buttons.items():
            widget.setEnabled(False)

        layout = QtWidgets.QVBoxLayout(self)
        widget = panels["icon_panel"]
        widget.setEnabled(False)
        layout.addWidget(widget)
        layout.addWidget(panels["icon_info"])


        widget = widgets["progress"]
        layout.addWidget(widget)
        widget.setFormat("loading %v/%m")


        widget = panels["icon_panel"]
        layout = QtWidgets.QHBoxLayout(panels["icon_panel"])
        layout.addWidget(widgets["icon_tree"])
        layout.addWidget(panels["list_panel"])
        widget.setStretchFactor(0, 28)
        widget.setStretchFactor(1, 71)

        control.was_qt_icon_loaded.connect(self.on_icon_loaded)
        control.was_qt_icon_added.connect(self.on_icon_added)
        control.load_qt_icons()

        widget = widgets["icon_tree"]
        widget.setAlternatingRowColors(True)
        widget.setAnimated(True)
        widget.setIndentation(16)
        widget.setEditTriggers(widget.NoEditTriggers)
        widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)

        def cat_tree_change(selected, deselected):
            if not selected.indexes():
                return
            index = selected.indexes()[0]
            cat_tree = [index.data()]
            current_index = index
            while current_index.parent().data():
                current_index = current_index.parent()
                cat_tree.insert(0, current_index.data().lower())

            self.widgets["search"].setText("/".join(cat_tree))

        # keep reference to sel model to avoid crash in pyside
        # https://stackoverflow.com/questions/19211430/pyside-segfault-when-using-qitemselectionmodel-with-qlistview
        sel_model = widget.selectionModel()
        sel_model.selectionChanged.connect(cat_tree_change)


        layout = QtWidgets.QVBoxLayout(panels["list_panel"])
        widget = widgets["search"]
        if __qtbind__ == "PySide2":
            widget.setClearButtonEnabled(True)
        widget.setPlaceholderText("search")
        layout.addWidget(widget)
        widget = widgets["icon_list"]
        widgets["notification"].setParent(widget)


        layout.addWidget(widget)

        widget.setIconSize(QtCore.QSize(24,24))
        widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        widget.setEditTriggers(widget.NoEditTriggers)
        widget.setViewMode(widget.IconMode)
        widget.setUniformItemSizes(True)
        widget.setResizeMode(widget.Adjust)
        widget.setMovement(widget.Static)
        widget.setSelectionMode(widget.ExtendedSelection)

        _model = models["icon"]
        deg = delegate.QtIconDelegate(_model)
        widget.setItemDelegate(deg)


        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(_model)
        proxy.setDynamicSortFilter(True)
        proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxy.setSortRole(model.IconName)
        proxy.setFilterRole(model.IconName)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        QtCore.QObject.connect(widgets["search"], QtCore.SIGNAL(
            "textChanged(QString)"), proxy.setFilterRegExp)

        widgets["icon_list"].setModel(proxy)


        def icon_changed(current, old):
            indexes = current.indexes()
            if not indexes:
                return
            index = indexes[0]
            icon = index.data(model.Object)
            icon_names = icon.icons
            count = len(icon_names)
            self.widgets["icon_count"].setText(
                str(count)+" size" + ("s" if count > 1 else ""))
            self.widgets["icon_names"].model().setStringList(icon_names)
            self.widgets["icon_names"].setCurrentIndex(0)

            for name, widget in self.buttons.items():
                widget.setEnabled(True)
            self.buttons["open_file"].setEnabled(os.path.exists(icon_names[0]))

        sel_model = widget.selectionModel()
        sel_model.selectionChanged.connect(icon_changed)
        widget.doubleClicked.connect(self.copy_name)

        layout = QtWidgets.QHBoxLayout(panels["icon_info"])
        widget = widgets["icon_names"]
        widget.setModel(QStringListModel())
        layout.addWidget(widget)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Preferred)
        widget = widgets["icon_count"]
        widget.setMinimumWidth(50)
        layout.addWidget(widget)
        widget = buttons["copy_text"]
        widget.setToolTip("copy icon string to clipboard")
        widget.setIcon(QtGui.QIcon(data.icons["copy"]))
        layout.addWidget(widget)
        widget.clicked.connect(self.copy_name)
        widget = buttons["open_file"]
        widget.clicked.connect(self.open_file)
        widget.setToolTip("open icon in explorer")
        widget.setIcon(QtGui.QIcon(data.icons["folder"]))
        layout.addWidget(widget)
        widget = buttons["save_file"]
        widget.clicked.connect(self.save_icons)
        widget.setToolTip("save icon to file")
        widget.setIcon(QtGui.QIcon(data.icons["save"]))
        layout.addWidget(widget)
        widget = buttons["view_file"]
        widget.setToolTip("show current icon")
        widget.setIcon(QtGui.QIcon(data.icons["eye"]))
        widget.clicked.connect(self.show_icon)
        layout.addWidget(widget)

        self.models = models
        self.control = control
        self.widgets = widgets
        self.buttons = buttons
        self.panels = panels

    def contextMenuEvent(self, event):
        self.menu = QtWidgets.QMenu(self)
        copy = QtWidgets.QAction(QtGui.QIcon(data.icons["copy"]),'copy text', self)
        copy.triggered.connect(self.copy_name)
        self.menu.addAction(copy)
        open = QtWidgets.QAction(QtGui.QIcon(data.icons["folder"]),'open folder', self)
        open.setEnabled(os.path.exists(self.widgets["icon_names"].currentText()))
        open.triggered.connect(self.open_file)
        self.menu.addAction(open)
        save = QtWidgets.QAction(QtGui.QIcon(data.icons["save"]),'save icons', self)
        save.triggered.connect(self.save_icons)
        self.menu.addAction(save)
        show = QtWidgets.QAction(QtGui.QIcon(data.icons["eye"]),'show icon', self)
        show.triggered.connect(self.show_icon)
        self.menu.addAction(show)


        self.menu.popup(QtGui.QCursor.pos())

    def on_icon_added(self,total,current):
        widget = self.widgets["progress"]
        widget.setRange(0,total)
        widget.setValue(current+1)

    def on_icon_loaded(self,icons,tree):
        for icon in icons:
            self.models["icon"].append(icon)
        self.widgets["icon_tree"].set_data(tree)

        self.widgets["progress"].setVisible(False)
        self.panels["icon_panel"].setEnabled(True)

    def show_icon(self):
        icon_file = self.get_current_icon_path(large=True)
        widget = IconPreviewer(self)
        widget.show(icon_file)

    def get_current_icon_path(self, large=False):
        widget = self.widgets["icon_names"]
        if large:
            return [widget.itemText(i) for i in range(widget.count())][-1]
        return widget.currentText()

    def open_file(self):
        icon_path = os.path.realpath(self.widgets["icon_names"].currentText())
        if os.path.exists(icon_path):
            subprocess.Popen('explorer /select, "%s" ' % icon_path)

    def save_icons(self):
        save_dir = QtWidgets.QFileDialog.getExistingDirectory()
        if not save_dir:
            self.widgets["notification"].show("canceled")
            return
        indexes = self.widgets["icon_list"].selectionModel().selectedIndexes()
        keep_structure = len(indexes)>1
        if keep_structure:
            for index in indexes:
                icons = index.data(model.Object).icons
                for icon in icons:
                    if icon.startswith(":/"):
                        file = icon[2:]
                    else:
                        file = icon
                        for sdir in data.new_custom_icon_path:
                            if re.match(sdir, file, flags=re.IGNORECASE):
                                file = re.sub(sdir, "", file)
                                break
                    icon_path = os.path.join(save_dir, file)
                    folder = os.path.dirname(icon_path)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    pixelmap = QtGui.QPixmap(icon)
                    pixelmap.save(icon_path, "PNG")
        else:
            icons = indexes[0].data(model.Object).icons
            for icon in icons:
                file = icon
                if icon.startswith(":/"):
                    file = icon[2:]
                icon_path = os.path.join(save_dir, os.path.basename(file))
                pixelmap = QtGui.QPixmap(icon)
                pixelmap.save(icon_path, "PNG")


    def copy_name(self):
        clipboard = QtGui.QClipboard()
        name = self.widgets["icon_names"].currentText()
        if not name.startswith(":/"):
            for sdir in data.new_custom_icon_path:
                if re.match(sdir, name, flags=re.IGNORECASE):
                    # remove folder
                    name = re.sub(sdir, "", name)
                    # remove size and .png
                    name = re.sub("(.*?)(_\d+)?.png", r"\1", name)
                    break
        clipboard.setText(name)
        self.widgets["notification"].show("<b>copyed</b> "+name)


class AtlasIconPage(QtWidgets.QWidget):
    def __init__(self,control, parent=None):
        super(AtlasIconPage, self).__init__(parent)

        self.control = control

        panels = {
            "icon_panel": QtWidgets.QWidget(),
            "icon_info": QtWidgets.QGroupBox("details"),
            "icon_usage": QtWidgets.QGroupBox("usage"),
        }

        widgets = {
            "search": QtWidgets.QLineEdit(),
            "icon_list": view.AtlasIconView(),

            # icon info
            "icon_names": QtWidgets.QComboBox(),
            "icon_count": QtWidgets.QLabel("0 size"),
            "open_file": QtWidgets.QToolButton(),
            "icon_usage": QtWidgets.QLabel(),

        }

        models = {
            "icon":model.AtlasIconModel()
        }

        for name, widget in widgets.items():
            widget.setObjectName(name)

        layout = QtWidgets.QVBoxLayout(self)

        for name, panel in panels.items():
            layout.addWidget(panel)

        control.was_atlas_icon_loaded.connect(self.on_icon_loaded)
        control.load_atlas_icons()


        layout = QtWidgets.QVBoxLayout(panels["icon_panel"])
        widget = widgets["search"]
        if __qtbind__ == "PySide2":
            widget.setClearButtonEnabled(True)
        widget.setPlaceholderText("search")
        layout.addWidget(widget)

        widget = widgets["icon_list"]
        widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        widget.setEditTriggers(widget.NoEditTriggers)
        widget.setResizeMode(widget.Adjust)
        widget.setMovement(widget.Static)
        layout.addWidget(widget)

        _model = models["icon"]

        proxy = QSortFilterProxyModel()
        proxy.setDynamicSortFilter(True)
        proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxy.setSourceModel(_model)
        proxy.setSortRole(model.IconName)
        proxy.setFilterRole(model.IconName)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        QtCore.QObject.connect(widgets["search"], QtCore.SIGNAL(
            "textChanged(QString)"), proxy.setFilterRegExp)

        widget.setModel(proxy)
        deg = delegate.AtlasIconDelegate(_model)
        widget.setItemDelegate(deg)
        widget.clicked.connect(self.update_detail)


        layout = QtWidgets.QGridLayout(panels["icon_info"])
        widget = widgets["icon_names"]
        layout.addWidget(widget, 0, 0)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Preferred)
        widget = widgets["icon_count"]
        widget.setMinimumWidth(50)
        layout.addWidget(widget, 0, 1)
        widget = widgets["open_file"]
        widget.clicked.connect(self.open_file)
        widget.setToolTip("open icon in explorer")
        widget.setIcon(QtGui.QIcon(data.icons["folder"]))
        layout.addWidget(widget, 0, 2)

        layout = QtWidgets.QHBoxLayout(panels["icon_usage"])
        widget = widgets["icon_usage"]
        widget.setText("")
        widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(widget)

        self.panels = panels
        self.widgets = widgets
        self.models = models

    def on_icon_loaded(self,icons):
        for icon in icons:
            self.models["icon"].append(icon)

    def update_detail(self, index):
        icon = index.data(model.Object)
        if not icon or icon.selected==None:
            return
        self.widgets["icon_count"].setText(str(icon.count)+" size" + ("s" if icon.count > 1 else ""))
        self.widgets["icon_names"].setModel(QStringListModel(icon.icon_images))

        usage = """<font color="#AAAAAA">icon:#("%s",%s) </font>""" % (icon.name, icon.selected+1)
        if icon.selected == 0:
            usage += """ or <font color="#AAAAAA">icon:"%s"</font>""" % icon.name

        self.widgets["icon_usage"].setText(usage)

    def open_file(self):
        subprocess.Popen('explorer /select, "%s" ' %
                         self.widgets["icon_names"].currentText())




class AboutPage(QtWidgets.QWidget):
    def __init__(self,control, parent=None):
        super(AboutPage, self).__init__(parent)

        self.control = control

        layout = QtWidgets.QVBoxLayout(self)

        widgets = {
            "text":QtWidgets.QTextBrowser()
        }

        widget = widgets["text"]

        widget.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        widget.setOpenExternalLinks(True)

        icon_paths = "<hr><b>icon search paths</b><ul>"
        for p in (list(data.new_custom_icon_path) + list(data.qt_icon_path) + list(data.old_icon_path)):
            p = os.path.realpath(p).lower()
            icon_paths += """<li><a href="%s">%s</a></li>""" % (p,p)
        icon_paths +="</ul>"

        author_info = """
            <pre><b>author : </b> kns002<br><b>version: </b> 0.02 <font color="#777777">(3ds max 2017+)</font><br><b>github : </b> <a href="https://github.com/knsii">https://github.com/knsii</a></pre>
        """
        widget.setText(
        """
            <style>
                * {line-height:1.1em}
                a {text-decoration:none;color:#AAAAAA}
                c {color:#999999;padding:2px}
                ul {list-style-type:none}
            </style>
            <b>useful links</b>
            <ul>
                <li><a href="https://help.autodesk.com/view/3DSMAX/2018/ENU/?guid=__developer_icon_guide_icon_guide_html">3ds max compiled icon resource guide</a></li>
                <li><a href="https://help.autodesk.com/view/3DSMAX/2017/ENU/?guid=GUID-4DAB2887-8436-4AAF-8081-81C32A3DEDA2">customize icons</a></li>
            </ul>
            <div></div>
            <b>show icon path in script listener</b>
            <ul>
                <li>enable: <c>customcontrolsoptions.printiconpaths=true</c></li>
                <li>disable: <c>customcontrolsoptions.printiconpaths=false</c></li>
            </ul>
        """+icon_paths+author_info

        )
        layout.addWidget(widget)
