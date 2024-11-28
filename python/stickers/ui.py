# *-* coding: utf-8 *-*
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
        self.frame_type = 0

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.dirname(__file__), "sticker_simple.ui"))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        self.ui.setParent(self)
        self.ui.layout().setContentsMargins(6, 6, 6, 6)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui)
        self.resize(self.ui.size())
        self.setLayout(layout)

    def create_connections(self):
        self.ui.folder_path_pb.clicked.connect(self.select_file)
        self.ui.geometry_pb.clicked.connect(self.set_geometry)
        self.ui.create_pb.clicked.connect(self.create_sticker)
        self.ui.cancel_pb.clicked.connect(self.close)
        self.ui.single_img_rb.toggled.connect(self.set_frame_type)
        self.ui.image_seq_rb.toggled.connect(self.set_frame_type)
        self.ui.multi_pose_rb.toggled.connect(self.set_frame_type)

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
        definition["file_path"] = self.ui.folder_path_le.text()
        definition["is_sequence"] = self.get_sequence_type()

        # Get all layers from the list widget
        definition["layers"] = [{"layerName": "base"}]

        # Get all maps from the list widget
        definition["maps"] = ["color"]

        return definition

    #    _    _ _____   ______                _   _
    #   | |  | |_   _| |  ____|              | | (_)
    #   | |  | | | |   | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
    #   | |  | | | |   |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
    #   | |__| |_| |_  | |  | |_| | | | | (__| |_| | (_) | | | \__ \
    #    \____/|_____| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
    #
    def set_frame_type(self):
        radio_button = self.sender()
        radio_text = str(radio_button.text()).replace(" ","")
        if radio_button.isChecked():
            self.frame_type = radio_text

    def get_sequence_type(self):
        seq_type_dict = {
            "SingleImage":0,
            "ImageSequence":1,
            "MultiPose":2
        }
        return seq_type_dict.get(self.frame_type,0)

    def set_geometry(self):
        """Set the geometry field to the selected object"""
        vertex_selected = cmds.ls(selection=True)[0]
        self.ui.geometry_le.setText(vertex_selected)

    def set_message_text(self, message):
        self.ui.message_lbl.setText(message)
        QtCore.QTimer.singleShot(4000, self.clean_message_text)

    def clean_message_text(self):
        self.ui.message_lbl.setText("")

    def select_file(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "Images (*.png *.xpm *.jpg)"
        )[0]
        self.ui.folder_path_le.setText(fileName)
