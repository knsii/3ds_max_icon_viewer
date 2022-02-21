import os
import re
import glob
from collections import OrderedDict as odict

from .qt import QtCore

from . import data
from . import utils


class IconViewerController(QtCore.QObject):
    was_qt_icon_loaded = QtCore.Signal(list,dict)
    was_qt_icon_added = QtCore.Signal(int,int)

    was_atlas_icon_loaded = QtCore.Signal(list)
    was_atlas_icon_added = QtCore.Signal(int,int)

    def __init__(self):
        super(IconViewerController,self).__init__()


    def load_qt_icons(self):
        def fetch_icon():
            icons,tree = self.get_qt_icons()
            self.was_qt_icon_loaded.emit(icons,tree)
        utils.run_thread(fetch_icon)


    def load_atlas_icons(self):
        def fetch_icon():
            icons = self.get_atlas_icons()
            self.was_atlas_icon_loaded.emit(icons)
        utils.run_thread(fetch_icon)


    def get_icon_name_from_path(self,path):
        for sdir in data.new_custom_icon_path:
            if re.match(sdir, path, flags=re.IGNORECASE):
                # remove folder
                path = re.sub(sdir, "", path)
                # remove size and .png
                path = re.sub("(.*?)(_\d+)?.png", r"\1", path)
                break
        return path


    def get_qt_icons(self):
        for qrcc in data.qt_icon_path:
            QtCore.QResource.registerResource(qrcc)
        images = []

        for sdir in data.new_custom_icon_path:
            dit = QtCore.QDirIterator(sdir, flags=QtCore.QDirIterator.Subdirectories)
            while dit.hasNext():
                info = dit.fileInfo()
                path = info.absoluteFilePath()
                if info.isFile() and path.endswith(".png"):
                    images.append(path)
                dit.next()

        dit = QtCore.QDirIterator(":/", flags=QtCore.QDirIterator.Subdirectories)
        while dit.hasNext():
            info = dit.fileInfo()
            path = info.absoluteFilePath()
            # ignore these icons
            if path.startswith((":/qt-project.org",":/Icons")):
                dit.next()
                continue
            if info.isFile() and path.endswith(".png"):
                images.append(path)
            dit.next()

        filtered = dict()
        for image in images:
            result = re.match("(.*)_(\d+x?\d+)?(.png)", image)
            if result is None:
                key = image[:-4]
                filtered[key] = None
            else:
                groups = result.groups()
                key = groups[0]
                size = groups[1]
                if not filtered.get(key,None):
                    filtered[key] = [size]
                else:
                    filtered[key].append(size)

        icons = []

        filtered_items = list(filtered.items())
        filtered_count = len(filtered_items)
        for i in range(filtered_count):
            name, sizes = filtered_items[i]
            if sizes is None:
                names = [name + ".png"]
            else:
                names = sorted([name + "_" + size + ".png" for size in sizes])
            count = len(names)
            icon_to_show = names[-1] if count <3 else names[1]

            name = self.get_icon_name_from_path(name)

            icons.append(
                data.QtIcon({
                    "name": name,
                    "icon":icon_to_show,
                    "icons": names,
                })

            )
            self.was_qt_icon_added.emit(filtered_count,i)

        cat_tree = odict()
        for name in sorted(filtered.keys()):
            name = name.lower()
            if name.startswith(":/"):
                name = name.replace(":/", "")
            else:
                for sdir in data.new_custom_icon_path:
                    name = name.replace(sdir.lower(), "")
            cats = name.split("/")[:-1]
            root = cat_tree
            for cat in cats:
                if cat in root:
                    root = root[cat]
                else:
                    root[cat] = {}
                    root = root[cat]

        return icons,cat_tree



    def get_atlas_icons(self):
        icon_files = []
        for p in data.old_icon_path:
            icon_files += glob.glob(p + "/*.bmp")

        icon_dict = dict()

        for icon in icon_files:
            icon = os.path.realpath(icon)
            file_name = os.path.basename(icon)
            result = re.match(
                "(.*)_(\d+)([ai]).bmp", file_name, flags=re.IGNORECASE)
            if result is None:
                continue
            icon_name, icon_size, icon_type = result.groups()
            if not icon_name in icon_dict:
                icon_dict[icon_name] = dict()
            if not icon_size in icon_dict[icon_name]:
                icon_dict[icon_name][icon_size] = dict()
            icon_dict[icon_name][icon_size][icon_type] = icon

        icons = list()
        for key, value in icon_dict.items():
            icons.append(
                data.AtlasIcon({
                    "name": key,
                    "icon": value
                })
            )

        return icons

