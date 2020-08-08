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

setting_path = 'C:/Users/jaec/PycharmProjects/light_library/light_library'
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


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class CustomListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
    
    def update_list_items(self):
        pass
    
    def all_items(self):
        pass
    
    def all_items_by_name(self):
        pass
    
    def delete_item_by_name(self, name):
        pass
        
    def select_item_by_name(self, name):
        pass

    def get_index_from_name(self, name):
        pass    

    def selected_items_by_name(self):
        pass
        
    def set_multi_selection(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)


class LightingToolDialog(QtWidgets.QDialog):
    UI_NAME = "LightingTool"
    ui_instance = None

    def __init__(self, parent=maya_main_window()):
        super(LightingToolDialog, self).__init__(parent)
        self.WINDOW_NAME = "Lighting Editor Extension V.1"

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

        self.setFixedWidth(600)
        self.setMinimumHeight(800)
        
        cmds.select(d=1)
        self.selected = []
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.event_id = ''
        self.scene_lights = get_scene_lights()
        self.light_attributes_widgets = OrderedDict() 
        self.light_visibilities_widgets = OrderedDict() 
        self.light_transforms_widgets = OrderedDict() 
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.selection_changed_callback = om.MEventMessage.addEventCallback("SelectionChanged", self.maya_selection_changed)
        
    def create_widgets(self):    
        self.light_list_widget = QtWidgets.QListWidget()
        self.light_list_widget.setFixedHeight(150)
        self.light_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.light_list_widget.addItems(self.scene_lights)
        
        self.light_info_group = QtWidgets.QGroupBox("SELECTION INFO")
        self.light_name = QtWidgets.QLabel("Light Name: %s "%(self.selected_light_name))
        self.light_type = QtWidgets.QLabel("Type: %s"%(self.selected_light_type))
        
        self.light_rename = QtWidgets.QLineEdit()
        
        self.btns = [self.set_icon_btn(key, value.get('icon')) for key, value in light_list.items()]
        
        self.attrib_group = QtWidgets.QGroupBox('ATTRIBUTES')
        for attrib_name, value in light_attributes.items():
            self.light_attributes_widgets.update({attrib_name : self.widget_checker(value.get('name'),value)})
        
        self.visibility_group = QtWidgets.QGroupBox('VISIBILITY')
        for attrib_name, value in light_visibilities.items():
            self.light_visibilities_widgets.update({attrib_name: self.widget_checker(value.get('name'),value)})        

        self.transform_group = QtWidgets.QGroupBox('TRANSFORM')
        for attrib_name, value in light_transforms.items():
            self.light_transforms_widgets.update({attrib_name: self.widget_checker(value.get('name'),value)})        

    def create_layout(self):
        widget = QtWidgets.QWidget()
        widget.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.light_info_layout = QtWidgets.QVBoxLayout()
        self.light_info_layout.addWidget(self.light_name)
        self.light_info_layout.addWidget(self.light_type)
        self.light_info_group.setLayout(self.light_info_layout)

        btnLayout01 = FlowLayout()
        map(btnLayout01.addWidget, self.btns)

        self.attrib_layout = QtWidgets.QVBoxLayout()
        for attrib_name, values in self.light_attributes_widgets.items():
            if values:
                self.attrib_layout.addWidget(values.get('layout'))
        self.attrib_group.setLayout(self.attrib_layout)
        self.attrib_layout.setSpacing(2);

        self.vis_layout = QtWidgets.QVBoxLayout()    
        for attrib_name, values in self.light_visibilities_widgets.items():
            if values:
                self.vis_layout.addWidget(values.get('layout'))
        self.visibility_group.setLayout(self.vis_layout)
        
        self.transform_layout = QtWidgets.QVBoxLayout()    
        for attrib_name, values in self.light_transforms_widgets.items():
            if values:
                self.transform_layout.addWidget(values.get('layout'))
        self.transform_group.setLayout(self.transform_layout)

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
        [btn.clicked.connect(partial(set_light,light_type = light_list[btn.text()].get('type'))) for btn in self.btns]
    
        
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
            self.light_selected()

                
    def attrib_setter_not_selected(self,*args):    
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.light_name.setText("Light Name: %s "%(self.selected_light_name))
        self.light_type.setText("Type: %s"%(self.selected_light_type))
        self.widget_setter(self.light_attributes_widgets)
        self.widget_setter(self.light_visibilities_widgets)
        self.widget_setter(self.light_transforms_widgets)
        self.light_selected()
    
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
        
    def light_selected(self):
        self.light_list_widget.clearSelection()
        update_light_list(self.light_list_widget)
        if self.selected:
            for selected in self.selected:
                try:
                    self.light_list_widget.findItems(selected.partialPathName(),QtCore.Qt.MatchExactly)[0].setSelected(1)
                except:
                    pass
        
        
    def maya_selection_changed(self,*args, **kwargs):
        try:
            sel = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(sel)
            selection_iter = om.MItSelectionList(sel)
            obj = om.MObject()

            if self.event_id:
                om.MMessage.removeCallback(self.event_id)
            self.event_id = om.MNodeMessage.addAttributeChangedCallback(obj, self.maya_attrib_changed)

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
        
    def maya_attrib_changed(self, *args, **kwargs):
        try:
            changed_attrib = args[1]
            self.attrib_update(changed_attrib)
        except RuntimeError, err:
            print err
            
        
    def closeEvent(self, event):    
        try:
            om.MMessage.removeCallback(self.selection_changed_callback)
            om.MMessage.removeCallback(self.event_id)
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



