# *-* coding: utf-8 *-*
# Copyright (C) 2023 Antaruxa S.L - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by:
# Andrés Méndez del Río <andres.mendez@antaruxa.com>, 2023
# Cristina Fernandez Gomez <cristina.fernandez@antaruxa.com>, 2023

"""Use of the UI

    1. Seleccionamos el vertice donde queremos colocar el sticker
    2. Rellenamos los campos:
        - Name: nombre del sticker Ej: "eye", "mouth", "nose"
        - Flag: flag del sticker Ej: "C", "L", "R"
        - Index: index del sticker Ej: 0, 1, 2
        - Layers: capas del sticker Ej: "base", "pupil", "iris"
          (Se puede añadir dandole al boton add, o presionando Enter)
          (Se pueden añadir mas de una layer a la vez, separandolas por una coma ',')
    3. Click en "Create" y creara el sticker

# Launch From Maya

import stickers.ui

try:
    sticker_ui.close()
    sticker_ui.deleteLater()
except:
    pass

sticker_ui = stickers.ui.StickerUI()
sticker_ui.show()
"""
import os
import sys

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtCore import QTimer
from shiboken2 import wrapInstance

from . import builder


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
        f = QtCore.QFile(os.path.join(os.path.dirname(__file__), "interface.ui"))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.ui_filepath_pb.clicked.connect(self.select_folder)
        self.ui.ui_vtx_pb.clicked.connect(self.set_geometry)
        self.ui.ui_createsticker_pb.clicked.connect(self.create_sticker)
        self.ui.ui_cancel_pb.clicked.connect(self.close)

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

    def set_message_text(self, message):
        self.ui.message_lbl.setText(message)
        QTimer.singleShot(4000, self.clean_message_text)

    def clean_message_text(self):
        self.ui.message_lbl.setText("")

    def select_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        self.ui.folder_path_le.setText(folder)
