import sys
import maya.OpenMaya as om
import maya.mel as mel

import maya.OpenMayaUI as omui

import maya.cmds as cmds
import os
import re
from functools import partial
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from collections import OrderedDict 

setting_path = '/Users/jaeyoungchoi/Workspace/lighting_library'
sys.path.append(setting_path)
sys.dont_write_bytecode=True

import settings 
reload(settings)
from settings import *

import light_lib_utils
reload(light_lib_utils)
from light_lib_utils import *

import FlowLayout
reload(FlowLayout)
from FlowLayout import FlowLayout

import ui_elements
reload(ui_elements)
from ui_elements import *


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class LightingToolDialog(QtWidgets.QDialog):
    UI_NAME = "LightingTool"
    ui_instance = None
    WINDOW_NAME = "Lighting Editor Extension V.1"
    WINDOW_SIZE = (600,800)
    
    def __init__(self, parent=maya_main_window()):
        super(LightingToolDialog, self).__init__(parent)
        self.dialog_setting()
        
        self.selected = []
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.scene_lights = get_scene_lights()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.attrib_changed_event_id = []
        self.selection_changed_event_id = om.MEventMessage.addEventCallback("SelectionChanged", self.maya_selection_changed)
    
    def dialog_setting(self):
        if cmds.window(self.UI_NAME, exists=True):
            cmds.deleteUI(self.UI_NAME, window=True)
        elif cmds.windowPref(self.UI_NAME, exists=True):
            cmds.windowPref(self.UI_NAME, remove=True)
        self.setObjectName(self.UI_NAME)
        self.setWindowTitle(self.WINDOW_NAME)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setFixedWidth(self.WINDOW_SIZE[0])
        self.setMinimumHeight(self.WINDOW_SIZE[1])
        cmds.select(d=1)
        
    def create_widgets(self):    
        self.light_list_widget = QtWidgets.QListWidget()
        self.light_list_widget.setFixedHeight(150)
        self.light_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.light_list_widget.addItems(self.scene_lights)
        
        self.light_name = QtWidgets.QLabel("Light Name: %s "%(self.selected_light_name))
        self.light_type = QtWidgets.QLabel("Type: %s"%(self.selected_light_type))
        
        self.light_rename = QtWidgets.QLineEdit()
        self.btns = [set_icon_btn(key, value.get('icon')) for key, value in light_list.items()]
        
        self.light_attributes_widgets = set_attribs_to_widgets(light_attributes)
        self.light_visibilities_widgets = set_attribs_to_widgets(light_visibilities)
        self.light_transforms_widgets = set_attribs_to_widgets(light_transforms)
        
    def create_layout(self):
        widget = QtWidgets.QWidget()
        widget.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.light_info_group = QtWidgets.QGroupBox("SELECTION INFO")
        self.light_info_layout = QtWidgets.QVBoxLayout()
        self.light_info_layout.addWidget(self.light_name)
        self.light_info_layout.addWidget(self.light_type)
        self.light_info_group.setLayout(self.light_info_layout)

        btnLayout01 = FlowLayout()
        map(btnLayout01.addWidget, self.btns)

        self.attrib_group = set_widgets_to_group(self.light_attributes_widgets,group_name = 'ATTRIBUTES')
        self.visibility_group = set_widgets_to_group(self.light_visibilities_widgets, group_name = 'VISIBILITY')
        self.transform_group = set_widgets_to_group(self.light_transforms_widgets, group_name = 'TRANSFORM')
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.attrib_group)
        layout.addWidget(self.visibility_group)
        layout.addWidget(self.transform_group)
        layout.addStretch()
        layout.setAlignment(QtCore.Qt.AlignTop)
        
        widget.setLayout(layout)
        
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollarea.setWidgetResizable(True)       
        self.scrollarea.setWidget(widget)
        self.scrollarea.setFocusPolicy(QtCore.Qt.NoFocus)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.light_list_widget)
        main_layout.addWidget(self.light_info_group)
        main_layout.addLayout(btnLayout01)
        main_layout.addWidget(self.scrollarea)
        
        num_of_attrib_widgets = len([key for key, value in self.light_attributes_widgets.items() if value])
        num_of_vis_widgets = len([key for key, value in self.light_visibilities_widgets.items() if value])
        num_of_trans_widgets = len([key for key, value in self.light_transforms_widgets.items() if value])
        self.attrib_group.resize(520,35*num_of_attrib_widgets)
        self.visibility_group.resize(520,35*num_of_vis_widgets)
        self.transform_group.resize(520,35*num_of_trans_widgets)
        
    def create_connections(self):
        self.light_list_widget.itemSelectionChanged.connect(lambda : select_light(self.light_list_widget))
        [btn.clicked.connect(partial(set_light,light_type = light_list[btn.text()].get('type'),list_widget = self.light_list_widget)) for btn in self.btns]
    
    def maya_selection_changed(self,*args, **kwargs):
        try:
            sel = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(sel)
            selection_iter = om.MItSelectionList(sel)
            obj = om.MObject()
            self.attrib_changed_event_id = self.set_attribute_changed_callback(obj)
            self.selected = []
            while not selection_iter.isDone():
                selection_iter.getDependNode(obj)
                dagPath = om.MDagPath.getAPathTo(obj)
                self.selected.append(dagPath)
                selection_iter.next()
            if selection_iter.isDone():
                update_light_list(self.light_list_widget)
                if self.selected:
                    self.attrib_setter_selected(self.selected)
                else:
                    self.attrib_setter_not_selected()
        except RuntimeError, err:
            print err    
        
    def set_attribute_changed_callback(self, obj):
        if self.attrib_changed_event_id:
            om.MMessage.removeCallback(self.attrib_changed_event_id)
        return om.MNodeMessage.addAttributeChangedCallback(obj, self.maya_attrib_changed)

    def maya_attrib_changed(self, *args, **kwargs):
        try:
            changed_attrib = args[1]
            self.attrib_update(changed_attrib)
        except RuntimeError, err:
            print err
            
    def attrib_setter_selected(self,selection,*args):
        selected = selection[-1]
        selected_full_name = selected.fullPathName()
        selected_name = selected.partialPathName()
        selected_type = cmds.objectType(selected_full_name)
        if selected_type == 'transform':
            selected_shape_type = cmds.objectType(cmds.listRelatives(selected_full_name,shapes=1))
        else:
            selected_shape_type = ''
        if 'light' in selected_type.lower() or 'light' in selected_shape_type.lower() :
            self.selected_light_name = selected_name
            self.selected_light_type = selected_type
            self.light_name.setText("Light Name: %s "%(self.selected_light_name))
            self.light_type.setText("Type: %s"%(self.selected_light_type))        
            self.widget_setter(self.light_attributes_widgets)
            self.widget_setter(self.light_visibilities_widgets)
            self.widget_setter(self.light_transforms_widgets)
            light_selected(self.light_list_widget, self.selected)

    def attrib_setter_not_selected(self,*args):    
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.light_name.setText("Light Name: %s "%(self.selected_light_name))
        self.light_type.setText("Type: %s"%(self.selected_light_type))
        self.widget_setter(self.light_attributes_widgets)
        self.widget_setter(self.light_visibilities_widgets)
        self.widget_setter(self.light_transforms_widgets)
        light_selected(self.light_list_widget, self.selected)
    
    def widget_setter(self,widgets_dict):
        for attrib, widgets in widgets_dict.items():
            if widgets:
                try:
                    if widgets_dict == self.light_transforms_widgets:
                        self.selected_light_name = self.selected_light_name if self.selected_light_name else cmds.ls(sl=1)[0]
                        if cmds.objectType(self.selected_light_name) != 'transform':
                            attrib_transform = cmds.listRelatives(self.selected_light_name, parent=True, fullPath=True)[0]
                        else:
                            attrib_transform = self.selected_light_name
                        attrib_value = cmds.getAttr('%s.%s'%(attrib_transform,attrib))    
                    else:
                        attrib_value = cmds.getAttr('%s.%s'%(self.selected_light_name,attrib))
                    attrib_value = round(attrib_value,3) if isinstance(attrib_value, float) else attrib_value
                    attrib_widgets = [widgets.get('widget'),widgets.get('label_widget')]
                    for attrib_widget in attrib_widgets[0]:
                        try:
                            attrib_widget.setChecked(attrib_value)
                            attrib_widget.setHidden(0)
                            attrib_widgets[1][0].setHidden(0)
                            continue
                        except:
                            pass
                        try:
                            attrib_widget.setValue(attrib_value)
                            attrib_widget.setHidden(0)
                            attrib_widgets[1][0].setHidden(0)
                            continue
                        except:
                            pass
                        try:
                            attrib_widget.maxLength()
                            attrib_widget.setText(str(attrib_value))
                            attrib_widget.setHidden(0)
                            attrib_widgets[1][0].setHidden(0)
                            continue
                        except:
                            pass
                    
                except:
                    pass

    def attrib_update(self,changed_attrib):
        if changed_attrib:
            if changed_attrib.name().split('.')[1] in light_attributes.keys():
                print changed_attrib.name()

    def closeEvent(self, event):    
        try:
            om.MMessage.removeCallback(self.selection_changed_event_id)
            om.MMessage.removeCallback(self.attrib_changed_event_id)
            print 'closed'
        except:
            pass
            

def main():
    try:
        lighting_tool.close()  # pylint : disable=E0601
        lighting_tool.deleteLater()
    except:
        pass

    lighting_tool = LightingToolDialog()
    lighting_tool.show()


if __name__ == "__main__":
    main()



