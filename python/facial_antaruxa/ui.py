# *-* coding: utf-8 *-*
import os
import sys

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
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


def delete_workspace_control(control):
    if cmds.workspaceControl(control, q=True, exists=True):
        cmds.workspaceControl(control, e=True, close=True)
        cmds.deleteUI(control, control=True)


class StickerUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    UI_NAME = "Create Sticker"

    def __init__(self, parent=maya_main_window()):
        delete_workspace_control(self.UI_NAME + "WorkspaceControl")
        super(StickerUI, self).__init__(parent)
        self.setWindowTitle("Sticker UI")
        self.setObjectName(self.__class__.UI_NAME)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(self.UI_NAME)
        self.resize(200, 300)

        # Set the layout of the window.
        self.setLayout(QtWidgets.QVBoxLayout())
        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        # Vertex related widgets
        self.ui_vtx_lb = QtWidgets.QLabel()
        self.ui_vtx_lb.setText("Vertex")

        self.ui_vtx_le = QtWidgets.QLineEdit()
        self.ui_vtx_le.setPlaceholderText("Set vertex origin")


        self.ui_vtx_pb = QtWidgets.QPushButton()
        self.ui_vtx_pb.setText("<<")

        self.ui_vtx_hl = QtWidgets.QHBoxLayout()
        self.ui_vtx_hl.addWidget(self.ui_vtx_le)
        self.ui_vtx_hl.addWidget(self.ui_vtx_pb)

        # Name related widgets
        self.ui_name_lb = QtWidgets.QLabel()
        self.ui_name_lb.setText("Name")

        self.ui_name_le = QtWidgets.QLineEdit()
        self.ui_name_le.setPlaceholderText("Sticker name")

        # Flag related widgets
        self.ui_flag_lb = QtWidgets.QLabel()
        self.ui_flag_lb.setText("Flag")

        self.ui_flag_le = QtWidgets.QLineEdit()
        self.ui_flag_le.setPlaceholderText("L, R, C ...")
    
        # Index related Widgets
        self.ui_index_lb = QtWidgets.QLabel()
        self.ui_index_lb.setText("Index")

        self.ui_index_spbx = QtWidgets.QSpinBox()
        self.ui_index_spc = QtWidgets.QSpacerItem(10,10,QtWidgets.QSizePolicy.Expanding,
                                                  QtWidgets.QSizePolicy.Minimum)

        self.ui_index_hl = QtWidgets.QHBoxLayout()
        self.ui_index_hl.addWidget(self.ui_index_spbx)
        self.ui_index_hl.addItem(self.ui_index_spc)

        # filepath related widgets
        self.ui_filepath_lb = QtWidgets.QLabel()
        self.ui_filepath_lb.setText("File Path")

        self.ui_filepath_le = QtWidgets.QLineEdit()
        self.ui_filepath_le.setPlaceholderText("Images path...")

        self.ui_filepath_pb = QtWidgets.QPushButton()
        self.ui_filepath_pb.setText("...")

        self.ui_filepath_hl = QtWidgets.QHBoxLayout()
        self.ui_filepath_hl.addWidget(self.ui_filepath_le)
        self.ui_filepath_hl.addWidget(self.ui_filepath_pb)

        # Imagesequence related widgets
        self.ui_imgsequence_cb = QtWidgets.QCheckBox()
        self.ui_imgsequence_cb.setText("Read as image sequence")

        # Main window buttons
        self.ui_cancel_pb = QtWidgets.QPushButton()
        self.ui_cancel_pb.setText("Cancel")
        self.ui_create_pb = QtWidgets.QPushButton()
        self.ui_create_pb.setText("Create")

        self.ui_mainbuttons_hl = QtWidgets.QHBoxLayout()
        self.ui_mainbuttons_hl.addWidget(self.ui_cancel_pb)
        self.ui_mainbuttons_hl.addWidget(self.ui_create_pb)

        

    def create_layout(self):
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui_vtx_lb)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui_vtx_hl)

        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.ui_name_lb)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ui_name_le)

        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.ui_flag_lb)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ui_flag_le)

        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.ui_index_lb)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.ui_index_hl)

        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.ui_filepath_lb)
        self.formLayout.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.ui_filepath_hl)

        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.ui_imgsequence_cb)

        self.layout().addLayout(self.formLayout)
        self.layout().addLayout(self.ui_mainbuttons_hl)

    def create_connections(self):
        pass


try:
    sticker_ui.close()
    sticker_ui.deleteLater()
except:
    pass
sticker_ui = StickerUI()
sticker_ui.show(dockable=True)

