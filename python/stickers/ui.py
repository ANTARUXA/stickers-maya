# *-* coding: utf-8 *-*
import os
import sys

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from . import builder
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtCore import QTimer
from shiboken2 import wrapInstance


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class StickerUI(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(StickerUI, self).__init__(parent)

        self.setWindowTitle("Sticker UI")
        self.builder = builder.Builder()
        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.dirname(__file__), "sticker_simple.ui"))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.folder_path_pb.clicked.connect(self.select_file)
        self.ui.del_layer_pb.clicked.connect(self.delete_layer)
        self.ui.geometry_pb.clicked.connect(self.set_geometry)
        self.ui.add_layer_pb.clicked.connect(self.add_layer)
        self.ui.create_pb.clicked.connect(self.create_sticker)
        self.ui.cancel_pb.clicked.connect(self.close)
        self.ui.add_layer_le.returnPressed.connect(self.add_layer)

        self.ui.add_map_le.returnPressed.connect(self.add_map)
        self.ui.add_map_pb.clicked.connect(self.add_map)
        self.ui.del_map_pb.clicked.connect(self.delete_map)

    #   ____ ____  _____    _  _____ _____   ____ _____ ___ ____ _  _______ ____
    #  / ___|  _ \| ____|  / \|_   _| ____| / ___|_   _|_ _/ ___| |/ / ____|  _ \
    # | |   | |_) |  _|   / _ \ | | |  _|   \___ \ | |  | | |   | ' /|  _| | |_) |
    # | |___|  _ <| |___ / ___ \| | | |___   ___) || |  | | |___| . \| |___|  _ <
    #  \____|_| \_\_____/_/   \_\_| |_____| |____/ |_| |___\____|_|\_\_____|_| \_\
    #
    def create_sticker(self):
        """
        Using base builder class, create a sticker with the data from the UI
        """
        definition = self.create_definition()
        self.builder._create_sticker(definition)

    def create_definition(self):
        """Fetch the data from the UI and return it as a dictionary"""
        definition = {}
        definition["geometry"] = self.ui.geometry_le.text()
        definition["name"] = self.ui.name_le.text()
        definition["flag"] = self.ui.flag_le.text()
        definition["file_path"] = self.ui.folder_path_le.text()
        definition["index"] = self.ui.index_sb.value()

        # Get all layers from the list widget
        definition["layers"] = []
        for item in range(self.ui.layers_lw.count()):
            definition["layers"].append(
                {"layerName": self.ui.layers_lw.item(item).text()}
            )

        # Get all maps from the list widget
        definition["maps"] = []
        for item in range(self.ui.maps_lw.count()):
            definition["maps"].append(self.ui.maps_lw.item(item).text())

        return definition

    #    _    _ _____   ______                _   _
    #   | |  | |_   _| |  ____|              | | (_)
    #   | |  | | | |   | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
    #   | |  | | | |   |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
    #   | |__| |_| |_  | |  | |_| | | | | (__| |_| | (_) | | | \__ \
    #    \____/|_____| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
    #

    def set_geometry(self):
        """Set the geometry field to the selected object"""
        vertex_selected = cmds.ls(selection=True)[0]
        self.ui.geometry_le.setText(vertex_selected)

    def delete_map(self):
        selected_items = self.ui.maps_lw.selectedItems()
        for item in selected_items:
            self.ui.maps_lw.takeItem(self.ui.maps_lw.row(item))

    def add_map(self):
        current_map_name = self.ui.add_map_le.text()
        if current_map_name == "":
            return
        if current_map_name.find(",") != -1:
            maps = current_map_name.split(",")
            for map in maps:
                self._add_map(map.strip())
            return
        self._add_map(current_map_name.strip())

    def _add_map(self, map_name):
        if self.check_duplicate_map(map_name):
            return
        new_item = QtWidgets.QListWidgetItem()
        new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
        new_item.setText(map_name)
        self.ui.maps_lw.addItem(new_item)
        self.ui.add_map_le.clear()

    def check_duplicate_map(self, new_map_name):
        if self.ui.maps_lw.findItems(new_map_name, QtCore.Qt.MatchExactly):
            self.set_message_text("New maps already exists".format(new_map_name))
            return True
        else:
            return False

    def add_layer(self):
        """Add a new layer to the list widget"""
        current_layer_name = self.ui.add_layer_le.text()
        if current_layer_name == "":
            return
        if current_layer_name.find(",") != -1:
            layers = current_layer_name.split(",")
            for layer in layers:
                self._add_layer(layer.strip())
            return
        self._add_layer(current_layer_name.strip())

    def check_duplicate_layer(self, new_layer_name):
        if self.ui.layers_lw.findItems(new_layer_name, QtCore.Qt.MatchExactly):
            self.set_message_text("New layers already exists".format(new_layer_name))
            return True
        else:
            return False

    def _add_layer(self, layer_name):
        if self.check_duplicate_layer(layer_name):
            return
        new_item = QtWidgets.QListWidgetItem()
        new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
        new_item.setText(layer_name)
        self.ui.layers_lw.addItem(new_item)
        self.ui.add_layer_le.clear()

    def delete_layer(self):
        selected_items = self.ui.layers_lw.selectedItems()
        for item in selected_items:
            self.ui.layers_lw.takeItem(self.ui.layers_lw.row(item))

    def set_message_text(self, message):
        self.ui.message_lbl.setText(message)
        QTimer.singleShot(4000, self.clean_message_text)

    def clean_message_text(self):
        self.ui.message_lbl.setText("")

    def select_file(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                       "Images (*.png *.xpm *.jpg)")[0]
        self.ui.folder_path_le.setText(fileName)


"""Show the UI
# If python3
# from importlib import reload
try:
    from facial_antaruxa.ui import sticker_simple as GUI

except:
    import sys
    sys.path.append('/home/andres.mendez/work/tools/studio/stickers/release/maya/scripts')
    from facial_antaruxa.ui import sticker_simple as GUI

try:
    sticker_ui.close()
    sticker_ui.deleteLater()
except:
    pass
reload(GUI)
sticker_ui = GUI.StickerUI()
sticker_ui.show()
"""

"""Use of the UI
1. Seleccionamos el vertice donde queremos colocar el sticker
2. Rellenamos los campos:
    - Name: nombre del sticker Ej: "eye", "mouth", "nose"
    - Flag: flag del sticker Ej: "C", "L", "R"
    - Index: index del sticker Ej: 0, 1, 2
    - Layers: capas del sticker Ej: "base", "pupil", "iris" (Se puede añadir dandole al boton add, o
      presionando enter) (Se pueden añadir mas de una layer a la vez, separandolas por una coma ',')
3. Click en "Create" y creara el sticker
"""
