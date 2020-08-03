import sys
import maya.OpenMaya as om
import maya.mel as mel

import maya.OpenMayaUI as omui

import maya.cmds as cmds
import os
import re

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from collections import OrderedDict 
light_attributes = OrderedDict() 
light_visibilities = OrderedDict() 
light_transforms = OrderedDict() 

light_attributes['decayRate']={'type':'combobox', 'items':['No Decay', 'Linear','Quadratic','Cubic'],'default':0}
light_attributes['aiUseColorTemperature']={'type':'checkbox','default': False}
light_attributes['color']={'type': 'rgb_slider','range':[0,1] ,'default':1}
light_attributes['intensity']={'type': 'float_slider','range':[0,10] ,'default':1}
light_attributes['aiColorTemperature']={'type': 'int_slider','range':[0,12000] ,'default':6500}
light_attributes['aiExposure']={'type': 'float_slider','range':[-5.0,5.0] ,'default':0}
light_attributes['aiSamples']={'type': 'int_slider','range':[0,10], 'default':1}
light_attributes['aiRadius']={'type': 'float_slider','range':[0,10], 'default':0}
light_attributes['aiShadowDensity']={'type': 'float_slider','range':[0,1] ,'default':1}
light_attributes['aiSpread']={'type': 'float_slider','range':[0,1] ,'default':1}
light_attributes['aiVolumeSamples']={'type': 'int_slider','range':[0,10] ,'default':2}
light_attributes['aiResolution']={'type': 'lineedit','default':512}
light_attributes['aiNormalize']={'type':'checkbox','default': True}
light_attributes['aiCastShadows']={'type':'checkbox','default': True}
light_attributes['emitDiffuse']={'type':'checkbox','default': True}
light_attributes['emitSpecular']={'type':'checkbox','default': True}
light_attributes['aiCastVolumetricShadows']={'type':'checkbox','default': True}

light_visibilities['aiDiffuse']={'type': 'float_slider','range':[0,1] ,'default':1}
light_visibilities['aiSpecular']={'type': 'float_slider','range':[0,1] ,'default':1}
light_visibilities['aiSss']={'type': 'float_slider','range':[0,1] ,'default':1}
light_visibilities['aiIndirect']={'type': 'float_slider','range':[0,1] ,'default':1}
light_visibilities['aiVolume']={'type': 'float_slider','range':[0,1] ,'default':1}
light_visibilities['aiMaxBounces']={'type': 'lineedit','default':999}
light_visibilities['aiAov']={'type': 'lineedit','default':'default'}

light_transforms['translateX']={'type': 'lineedit','default':0}
light_transforms['translateY']={'type': 'lineedit','default':0}
light_transforms['translateZ']={'type': 'lineedit','default':0}
light_transforms['rotateX']={'type': 'lineedit','default':0}
light_transforms['rotateY']={'type': 'lineedit','default':0}
light_transforms['rotateZ']={'type': 'lineedit','default':0}
light_transforms['scaleX']={'type': 'lineedit','default':1}
light_transforms['scaleY']={'type': 'lineedit','default':1}
light_transforms['scaleZ']={'type': 'lineedit','default':1}

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

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
        self.setMinimumHeight(450)
        
        cmds.select(d=1)
        self.selected = []
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.event_id = ''
        self.light_attributes_widgets = OrderedDict() 
        self.light_visibilities_widgets = OrderedDict() 
        self.light_transforms_widgets = OrderedDict() 
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.selection_changed_callback = om.MEventMessage.addEventCallback("SelectionChanged", self.maya_selection_changed)
        

    def create_widgets(self):
        self.light_list_refresh = QtWidgets.QPushButton('Refresh')
        
        self.light_info_group = QtWidgets.QGroupBox("CURRENT LIGHT INFO")
        self.light_name = QtWidgets.QLabel("Light Name: %s "%(self.selected_light_name))
        self.light_type = QtWidgets.QLabel("Type: %s"%(self.selected_light_type))
        
        
        self.attrib_group = QtWidgets.QGroupBox('ATTRIBUTES')
        for attrib_name, value in light_attributes.items():
            self.light_attributes_widgets.update({attrib_name : self.widget_checker(attrib_name,value)})
        
        self.visibility_group = QtWidgets.QGroupBox('VISIBILITY')
        for attrib_name, value in light_visibilities.items():
            self.light_visibilities_widgets.update({attrib_name: self.widget_checker(attrib_name,value)})        

        self.transform_group = QtWidgets.QGroupBox('TRANSFORM')
        for attrib_name, value in light_transforms.items():
            self.light_transforms_widgets.update({attrib_name: self.widget_checker(attrib_name,value)})        


    def create_layout(self):
        widget = QtWidgets.QWidget()
        
        self.light_info_layout = QtWidgets.QVBoxLayout()
        self.light_info_layout.addWidget(self.light_name)
        self.light_info_layout.addWidget(self.light_type)
        self.light_info_group.setLayout(self.light_info_layout)

        self.attrib_layout = QtWidgets.QVBoxLayout()
        for attrib_name, values in self.light_attributes_widgets.items():
            if values:
                self.attrib_layout.addLayout(values.get('layout'))
        self.attrib_group.setLayout(self.attrib_layout)
        
        self.vis_layout = QtWidgets.QVBoxLayout()    
        for attrib_name, values in self.light_visibilities_widgets.items():
            if values:
                self.vis_layout.addLayout(values.get('layout'))
        self.visibility_group.setLayout(self.vis_layout)
            
        self.transform_layout = QtWidgets.QVBoxLayout()    
        for attrib_name, values in self.light_transforms_widgets.items():
            if values:
                self.transform_layout.addLayout(values.get('layout'))
        self.transform_group.setLayout(self.transform_layout)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.light_info_group)
        layout.addWidget(self.light_list_refresh)
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
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scrollarea)
        
        num_of_attrib_widgets = len([key for key, value in self.light_attributes_widgets.items() if value])
        num_of_vis_widgets = len([key for key, value in self.light_visibilities_widgets.items() if value])
        num_of_trans_widgets = len([key for key, value in self.light_transforms_widgets.items() if value])
        self.attrib_group.resize(520,35*num_of_attrib_widgets)
        self.visibility_group.resize(520,35*num_of_vis_widgets)
        self.transform_group.resize(520,35*num_of_trans_widgets)
        
    def create_connections(self):
        pass
        
    def widget_checker(self,attrib_name, value):
        if value.get('type') == 'rgb_slider':
            pass
        elif value.get('type') =='float_slider':
            return self.float_slider_widget(attrib_name)
        elif value.get('type') =='int_slider':
            pass
        elif value.get('type') =='checkbox':
            return self.checkbox_widget(attrib_name)
        elif value.get('type') =='combobox':
            return self.combobox_widget(attrib_name, value.get('items'))
        elif value.get('type') =='lineedit':
            return self.lineedit_widget(attrib_name)
        
    def float_slider_widget(self,attrib_name=''):
        attrib_name_fixed = re.sub("([A-Z])"," \g<0>",attrib_name).capitalize()
        attrib_label = QtWidgets.QLabel(attrib_name_fixed+":")
        attrib_value = QtWidgets.QLineEdit()
        attrib_value.setFixedWidth(80)
        attrib_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        attrib_slider.setRange(0,10000)
        attrib_slider.setFixedWidth(250)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_value)
        attrib_block.addWidget(attrib_slider)
        attrib_block.addSpacing(50)
        attrib_value.setHidden(1)
        attrib_slider.setHidden(1)
        attrib_label.setHidden(1)
        return {'layout':attrib_block, 'label':attrib_name, 'widget' : [attrib_value, attrib_slider],'label_widget': [attrib_label]}
        
    def combobox_widget(self, attrib_name='', selection_list=[]):
        attrib_name_fixed = re.sub("([A-Z])"," \g<0>",attrib_name).capitalize()
        attrib_label = QtWidgets.QLabel(attrib_name_fixed+":")
        attrib_combobox = QtWidgets.QComboBox()
        attrib_combobox.addItems(selection_list)
        attrib_combobox.setFixedWidth(100)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_combobox)
        attrib_block.addSpacing(288)
        attrib_combobox.setHidden(1)
        attrib_label.setHidden(1)
        return {'layout':attrib_block, 'label':attrib_name, 'widget' : [attrib_combobox],'label_widget': [attrib_label]}

    def checkbox_widget (self, attrib_name='', num_of_cb = 1, cb_list = []):
        attrib_name_fixed = re.sub("([A-Z])"," \g<0>",attrib_name)
        attrib_checkbox = QtWidgets.QCheckBox(attrib_name_fixed)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addSpacing(35)
        attrib_block.addWidget(attrib_checkbox)
        attrib_block.addStretch()
        attrib_checkbox.setHidden(1)
        return {'layout':attrib_block,'label': attrib_name, 'widget' : [attrib_checkbox], 'label_widget': []}

    def lineedit_widget (self, attrib_name=''):
        attrib_name_fixed = re.sub("([A-Z])"," \g<0>",attrib_name)
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_lineedit = QtWidgets.QLineEdit()
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_lineedit)
        attrib_block.addSpacing(260)
        attrib_lineedit.setHidden(1)
        attrib_label.setHidden(1)
        return {'layout':attrib_block,'label': attrib_name, 'widget' : [attrib_lineedit], 'label_widget': [attrib_label]}
    
    def attrib_setter(self,*args):
        if self.selected:
            selected = self.selected[-1]
            selected_full_name = selected.fullPathName()
            selected_name = selected.partialPathName()
            selected_type = cmds.objectType(selected_full_name)
            if selected_type == 'transform':
                selected_shape_type = cmds.objectType(cmds.listRelatives(selected_full_name,shapes=1))
            if 'light' in selected_type.lower() or 'light' in selected_shape_type.lower() :
                self.selected_light_name = selected_name
                self.selected_light_type = selected_type
                self.light_name.setText("Light Name: %s "%(self.selected_light_name))
                self.light_type.setText("Type: %s"%(self.selected_light_type))        
                self.widget_setter(self.light_attributes_widgets)
                self.widget_setter(self.light_visibilities_widgets)
                self.widget_setter(self.light_transforms_widgets)
                        
        else :
            self.selected_light_name = ''
            self.selected_light_type = ''
            self.light_name.setText("Light Name: %s "%(self.selected_light_name))
            self.light_type.setText("Type: %s"%(self.selected_light_type))
            self.widget_setter(self.light_attributes_widgets)
            self.widget_setter(self.light_visibilities_widgets)
            self.widget_setter(self.light_transforms_widgets)
            
    def widget_setter(self,widgets_dict):
        for attrib, widgets in widgets_dict.items():
            if widgets:
                try:
                    if widgets_dict == self.light_transforms_widgets:
                        attrib_transform = cmds.listRelatives(self.selected_light_name, parent=True, fullPath=True)[0]
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
                self.attrib_setter()
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
    
    
"""
rgb_slider
float_slider
int_slider
checkbox
combobox
lineedit

"""

cmds.getAttr('aiAreaLightShape1.aiExposure')

a = 1.33
isinstance(a, float)