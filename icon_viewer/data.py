import os

from .qt import QtCore,QtGui

from . import utils

icons = {
    "eye":":/Common/Toggle/Visible_on_16.png",
    "save":":/Common/Save_16.png" if QtCore.QFile.exists(":/Common/Save_16.png") else ":/Common/Save_48.png",
    "folder":":/Common/Folder_16.png" if QtCore.QFile.exists(":/Common/Folder_16.png") else ":/GameExporter/BrowseFolder_16.png",
    "copy":":/CommandPanel/Motion/BipedRollout/MotionFlow/Paste_16.png",
}

maxui_lnpath = utils.get_max_dir("UI_ln")
usericon_path = utils.get_max_dir("usericons")

new_custom_icon_path = (
    os.path.join(maxui_lnpath, "icons/dark/"),
    os.path.join(maxui_lnpath, "icons/light/"),
    os.path.join(usericon_path, "dark/"),
    os.path.join(usericon_path, "light/"),
)
new_custom_icon_path = tuple(reversed(sorted([p.replace("\\", "/") for p in new_custom_icon_path], key=len)))

qt_icon_path = (
    os.path.join(maxui_lnpath, "iconslight.rcc"),
    os.path.join(maxui_lnpath, "iconsdark.rcc"),
)
old_icon_path = (
    usericon_path,
    maxui_lnpath+"/iconsdark/",
)


class QtIcon():
    def __init__(self, info):
        self.name = info.get("name",None)
        self.icons = info.get("icons",[])
        file = info.get("icon",None)

        if file:
            # use QImage to ensure thread safe https://doc.qt.io/qt-5/threads-modules.html
            image = QtGui.QImage(file)
            if max(image.width(),image.height())>24:
                image = image.scaled(24,24,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation)
            self.map = image
        else:
            self.map = None


class AtlasIcon():
    def __init__(self, info):
        self.name = info["name"]
        icons = info["icon"]
        self.sizes = sorted([int(k) for k in icons.keys()])
        self.count = len(self.sizes)

        self.image = icons[str(self.sizes[-1])].get("i", None)
        self.alpha = icons[str(self.sizes[-1])].get("a", None)
        self.icon_images = []
        for value in icons.values():
            if "i" in value:
                self.icon_images.append(value["i"])
        image = QtGui.QImage(self.image)
        if self.alpha:
            image.setAlphaChannel(QtGui.QImage(self.alpha))
        height = 24
        self.map = image.scaledToHeight(height, mode=QtCore.Qt.SmoothTransformation)
        self.name_width = height*7
        self.selected = None
