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

import pymel.core.datatypes as dt
import maya.OpenMaya as om
import maya.cmds as cmds

light_attributes = OrderedDict() 
light_visibilities = OrderedDict() 
light_transforms = OrderedDict() 
light_list = OrderedDict() 

light_attributes['decayRate']={'type':'combobox', 'items':['No Decay', 'Linear','Quadratic','Cubic'],'default':0, 'name':'Decay Rate'}
light_attributes['aiUseColorTemperature']={'type':'checkbox','default': False, 'name':'Use Color Temperature'}
light_attributes['color']={'type': 'rgb_slider','range':[0,1] ,'default':1, 'name':'Color'}
light_attributes['intensity']={'type': 'float_slider','range':[0,10] ,'default':1, 'name':'Intensity'}
light_attributes['aiColorTemperature']={'type': 'int_slider','range':[0,12000] ,'default':6500, 'name':'Temperature'}
light_attributes['aiExposure']={'type': 'float_slider','range':[-5.0,5.0] ,'default':0, 'name':'Exposure'}
light_attributes['aiSamples']={'type': 'int_slider','range':[0,10], 'default':1, 'name':'Samples'}
light_attributes['aiRadius']={'type': 'float_slider','range':[0,10], 'default':0, 'name':'Radius'}
light_attributes['aiShadowDensity']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Shadow Intensity'}
light_attributes['aiSpread']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Spread'}
light_attributes['aiVolumeSamples']={'type': 'int_slider','range':[0,10] ,'default':2, 'name':'Volume Samples'}
light_attributes['aiResolution']={'type': 'lineedit','default':512, 'name':'Resolution'}
light_attributes['emitDiffuse']={'type':'checkbox','default': True, 'name':'Emit Diffuse'}
light_attributes['emitSpecular']={'type':'checkbox','default': True, 'name':'Emit Specular'}
light_attributes['aiNormalize']={'type':'checkbox','default': True, 'name':'Normalize'}
light_attributes['aiCastShadows']={'type':'checkbox','default': True, 'name':'Cast Shadows'}
light_attributes['aiCastVolumetricShadows']={'type':'checkbox','default': True, 'name':'Cast Volumetric Shadows'}

light_visibilities['aiDiffuse']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Diffuse'}
light_visibilities['aiSpecular']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Specular'}
light_visibilities['aiSss']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'SSS'}
light_visibilities['aiIndirect']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Indirect'}
light_visibilities['aiVolume']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Volume'}
light_visibilities['aiMaxBounces']={'type': 'lineedit','default':999, 'name':'Max Bounces'}
light_visibilities['aiAov']={'type': 'lineedit','default':'default','name':'AOV Light Group'}

light_transforms['translate']={'type': 'lineedit_vector','default':0, 'name':'Translate X | Y | Z'}
light_transforms['rotate']={'type': 'lineedit_vector','default':0, 'name':'Rotate X | Y | Z'}
light_transforms['scale']={'type': 'lineedit_vector','default':1, 'name':'Scale X | Y | Z'}

light_list['Direct'] = {'type':'direct', 'icon':':/directionallight.png'}
light_list['Point'] = {'type':'point', 'icon':':/pointlight.png'}
light_list['Spot'] = {'type':'spot', 'icon':':/spotlight.png'}
light_list['Area'] = {'type':'area', 'icon':':/arealight.png'}


light_items = ['aiAreaLight',
             'aiAtmosphereVolume',
             'aiMeshLight',
             'aiPhotometricLight',
             'aiSkyDomeLight',
             'ambientLight',
             'areaLight',
             'directionalLight',
             'pointLight',
             'spotLight',
             'volumeLight'
             ]



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
        self.setMinimumHeight(800)
        
        cmds.select(d=1)
        self.selected = []
        self.selected_light_name = ''
        self.selected_light_type = ''
        self.event_id = ''
        self.scene_lights = self.get_scene_lights()
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
    
    def get_scene_lights(self):
        lights = []
        for light in light_items:
            lights+=cmds.ls(type=[light])
        lights = sorted(list(set(lights)))
        return lights
    
    def update_light_list (self):
        current_lights = self.get_scene_lights()
        if current_lights == self.scene_lights:
            return 0
        else:
            added = list(set(current_lights) - set(self.scene_lights))
            deleted = list(set(self.scene_lights) - set(current_lights))
        [self.light_list_widget.takeItem(self.light_list_widget.row(self.light_list_widget.findItems(d,QtCore.Qt.MatchExactly)[0])) for d in deleted]
        self.light_list_widget.addItems(added)
        self.scene_lights = current_lights
        
    def select_light(self):
        cmds.select([selected.text() for selected in self.light_list_widget.selectedItems()])

    def create_connections(self):
        self.light_list_widget.itemSelectionChanged.connect(self.select_light)
        [btn.clicked.connect(partial(self.set_light,light_type = light_list[btn.text()].get('type'))) for btn in self.btns]
    
    
    def set_light(self, light_type, *args):
        selection = cmds.ls(sl=1)
        if selection:
            if cmds.objectType(selection[0]) == 'transform':
                [self.create_light(light_type,selected, 'transform') for selected in selection]
            elif cmds.objectType(selection[0]) == 'mesh':
                self.create_light(light_type,selection,'mesh')
        self.update_light_list()
        
    
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
        elif value.get('type') =='lineedit_vector':
            return self.lineedit_vector_widget(attrib_name)        


    def float_slider_widget(self,attrib_name=''):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_value = QtWidgets.QLineEdit()
        attrib_value.setFixedWidth(80)
        attrib_value.setStyleSheet("background-color:rgb(40,40,40)")
        attrib_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        attrib_slider.setRange(0,10000)
        attrib_slider.setFixedWidth(250)
        attrib_slider.setStyleSheet("background-color:rgb(60,60,60)")
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_value)
        attrib_block.addWidget(attrib_slider)
        attrib_block.addSpacing(50)
        attrib_frame = QtWidgets.QFrame()
        attrib_frame.setLayout(attrib_block)
        attrib_frame.setStyleSheet("background-color:rgb(80,80,80);border-radius:3px;")
        return {'layout':attrib_frame, 'label':attrib_name, 'widget' : [attrib_value, attrib_slider],'label_widget': [attrib_label]}
        
    def combobox_widget(self, attrib_name='', selection_list=[]):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_combobox = QtWidgets.QComboBox()
        attrib_combobox.addItems(selection_list)
        attrib_combobox.setFixedWidth(100)
        attrib_combobox.setStyleSheet("background-color:rgb(60,60,60);")
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_combobox)
        attrib_block.addSpacing(288)
        attrib_frame = QtWidgets.QFrame()
        attrib_frame.setLayout(attrib_block)
        attrib_frame.setStyleSheet("background-color:rgb(80,80,80);border-radius:3px;")
        return {'layout':attrib_frame, 'label':attrib_name, 'widget' : [attrib_combobox],'label_widget': [attrib_label]}

    def checkbox_widget (self, attrib_name='', num_of_cb = 1, cb_list = []):
        attrib_checkbox = QtWidgets.QCheckBox(attrib_name)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addSpacing(35)
        attrib_block.addWidget(attrib_checkbox)
        attrib_block.addStretch()
        attrib_frame = QtWidgets.QFrame()
        attrib_frame.setLayout(attrib_block)
        return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_checkbox], 'label_widget': []}

    def lineedit_widget (self, attrib_name=''):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_lineedit = QtWidgets.QLineEdit()
        attrib_lineedit.setStyleSheet("background-color:rgb(40,40,40)")
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_lineedit)
        attrib_block.addSpacing(264)
        attrib_frame = QtWidgets.QFrame()
        attrib_frame.setLayout(attrib_block)
        attrib_frame.setStyleSheet("background-color:rgb(80,80,80);border-radius:3px;padding:0px;margin:0px;border:0px;")
        return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit], 'label_widget': [attrib_label]}

    def lineedit_vector_widget (self, attrib_name=''):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_lineedit = QtWidgets.QLineEdit()
        attrib_lineedit.setStyleSheet("background-color:rgb(40,40,40)")
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_lineedit)
        attrib_block.addSpacing(260)
        attrib_frame = QtWidgets.QFrame()
        attrib_frame.setLayout(attrib_block)
        attrib_frame.setStyleSheet("background-color:rgb(80,80,80);border-radius:3px;padding:0px;margin:0px;border:0px;")
        return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit], 'label_widget': [attrib_label]}
    
    def set_icon_btn(self, label, icon=':/ambientlight.png'):
        btn = QtWidgets.QToolButton()
        iconBtnMinSize = QtCore.QSize(200, 200)
        iconBtnSize = QtCore.QSize(200, 200)
        iconSize = QtCore.QSize(36, 36)
        btn.resize(iconBtnSize)
        btn.setIcon(QtGui.QIcon(icon))
        btn.setText(label)
        btn.setIconSize(iconSize)
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        btn.setFocusPolicy(QtCore.Qt.NoFocus)
        return btn
        
        
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
                
    def longest_length(self,vectors):
        max_length = [0,0,0]
        for i in range(len(vectors)-1):
            for j in range(i,len(vectors)):
                length = (vectors[i]-vectors[j]).length()
                if length > max_length[0]:
                    max_length = [length, i, j]
        return max_length[1], max_length[2]

    def farest_vector(self,start_vec, end_vec, vectors):
        farest_vec = [0,0]
        for i in range(len(vectors)):
            if vectors[i] in [start_vec,end_vec]:
                continue
            a = vectors[i]-start_vec
            b = end_vec-start_vec
            a_dot_b = a*b
            result = abs(a.length()*a.length() - (a_dot_b/b.length())*(a_dot_b)/b.length())
            if result > farest_vec[0]:
                farest_vec = [result, i]
        return farest_vec[1]
        
    def create_light(self,light_type, selected, obj_type):
        cmds.select(selected)
        selection = cmds.ls(sl=1)
        selection = cmds.polyListComponentConversion( selection, tf=True )
        cmds.select(selection)
        selection = cmds.ls(sl=1)
        cmds.selectMode(component=1)
        cmds.selectPref(useDepth=1)
        cmds.setToolTo('Move')
        pos = cmds.manipMoveContext('Move', query=True, position=True) 
        current_lights = self.get_scene_lights()
        if light_type == 'area':
            cmds.cmdArnoldAreaLights()
        elif light_type == 'spot':
            cmds.spotLight()
        elif light_type == 'point':
            cmds.pointLight()
        elif light_type == 'direct':
            return 0 
        
        added_lights = self.get_scene_lights()
        target_shape = list(set(added_lights) - set(current_lights))[0]
        
        
        target = cmds.listRelatives(target_shape, p=1)[0]
        
        
        if obj_type == 'mesh':
            vtxs = cmds.xform(selection, q=True, ws=True, t=True)
            vectors = [om.MVector(*vtxs[i:i + 3]) for i in range(0, len(vtxs), 3)]
            vectors_left = [om.MVector(*vtxs[i:i + 3]) for i in range(0, len(vtxs), 3)]
            
            start_vec_idx, end_vec_idx = self.longest_length(vectors)
            start_vec = vectors[start_vec_idx]
            end_vec = vectors[end_vec_idx]
            mid_vec_idx = self.farest_vector(start_vec, end_vec, vectors)
            mid_vec = vectors[mid_vec_idx]
            center_vec = om.MVector(*pos)-start_vec
            edge_vec_01 = mid_vec-start_vec
            edge_vec_02 = mid_vec-end_vec
            up_vec = edge_vec_02*(center_vec*edge_vec_02/(edge_vec_02.length()*edge_vec_02.length()))
            
            cmds.move(pos[0], pos[1], pos[2], target)

            constr = cmds.normalConstraint(selection, target, aimVector = (0,0,-1), wu = (up_vec.x,up_vec.y,up_vec.z), worldUpType= 2)
            cmds.delete(constr)

            cmds.setAttr(target+'.s',edge_vec_01.length()/2, edge_vec_02.length()/2, edge_vec_02.length()/2)
        elif obj_type == 'transform':
            cmds.move(pos[0], pos[1], pos[2], target)
            constr = cmds.normalConstraint(selection, target, aimVector = (0,0,-1), worldUpType= 2)
            cmds.delete(constr)
            cmds.setAttr(target+'.s', 10,10,10)
            
        select_tool = cmds.selectContext('Select Tool')
        cmds.setToolTo(select_tool)
        cmds.selectMode(object=1, component=False)

    def attrib_update(self,changed_attrib):
        if changed_attrib:
            if changed_attrib.name().split('.')[1] in light_attributes.keys():
                print changed_attrib.name()
        
    def light_selected(self):
        self.light_list_widget.clearSelection()
        self.update_light_list()
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
                self.update_light_list()
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
            

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.margin = margin
        
        # spaces between each item
        self.spaceX = 5
        self.spaceY = 5

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin, 2 * self.margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            # spaceX = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            # spaceY = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + self.spaceX
            if nextX - self.spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + self.spaceY
                nextX = x + item.sizeHint().width() + self.spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


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



