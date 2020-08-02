import sys
import maya.OpenMaya as om
import maya.mel as mel

import maya.OpenMayaUI as omui

import maya.cmds as cmds
import os

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


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
        self.setMinimumSize(520, 100)
        self.setMaximumSize(525, 825)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        
        self.selected = []
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.selection_changed_callback = om.MEventMessage.addEventCallback("SelectionChanged", self.maya_selection_changed)

    def create_widgets(self):
        self.light_list_refresh = QtWidgets.QPushButton('Refresh')
        
        self.attrib_group = QtWidgets.QGroupBox('ATTRIBUTES')
        self.attrib_kelbin = self.checkbox_widget("Kelvin")
        self.attrib_light_shape = self.combobox_widget('Light Shape',['disk','quad','cylinder'])
        self.attrib_color = self.float_slider_widget('Color')
        self.attrib_intensity = self.float_slider_widget('Intensity')
        self.attrib_exposure = self.float_slider_widget('Exposure')
        self.attrib_sample = self.float_slider_widget('Sample')
        self.attrib_normalize = self.checkbox_widget("Normalize")
        self.attrib_cast_shadows = self.checkbox_widget("Cast Shadows")
        self.attrib_cast_vol_shadows = self.checkbox_widget("Cast volumetric Shadows")
        
        self.visibility_group = QtWidgets.QGroupBox('VISIBILITY')
        self.visibility_group.setCheckable(1)
        
        self.vis_diffuse = self.float_slider_widget('Diffuse')
        self.vis_specular = self.float_slider_widget('Specular')
        self.vis_sss = self.float_slider_widget('SSS')
        self.vis_indirect = self.float_slider_widget('Indirect')
        self.vis_volume = self.float_slider_widget('Volume')
        self.vis_maxbounce = self.float_slider_widget('Max Bounces')
        # self.vis_aov_light_group = self.float_slider_widget('AOV Light Group')
        
        
    def create_layout(self):
        
        self.attrib_layout = QtWidgets.QVBoxLayout()
        self.attrib_layout.addLayout(self.attrib_kelbin.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_light_shape.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_color.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_intensity.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_exposure.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_sample.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_normalize.get('layout_widget'))
        self.attrib_layout.addLayout(self.attrib_cast_shadows.get('layout_widget'))
        self.attrib_group.setLayout(self.attrib_layout)

        vis_layout = QtWidgets.QVBoxLayout()
        vis_layout.addLayout(self.vis_diffuse.get('layout_widget'))
        vis_layout.addLayout(self.vis_specular.get('layout_widget'))
        vis_layout.addLayout(self.vis_sss.get('layout_widget'))
        vis_layout.addLayout(self.vis_indirect.get('layout_widget'))
        vis_layout.addLayout(self.vis_volume.get('layout_widget'))
        vis_layout.addLayout(self.vis_maxbounce.get('layout_widget'))        
        self.visibility_group.setLayout(vis_layout)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.light_list_refresh)
        layout.addWidget(self.attrib_group)
        layout.addWidget(self.visibility_group)
        
    def create_connections(self):
        self.visibility_group.toggled.connect(self.collapse_test)
    
    def collapse_test(self):
        if self.visibility_group.isChecked:
            self.attrib_group.setLayout(self.attrib_layout)
        else:
            self.attrib_group.setLayout()
        
    def float_slider_widget(self,attrib_name=''):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
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
        return {'layout_widget':attrib_block, 'label_widget':attrib_label, 'value_widget' : attrib_value, 'slider_widget':attrib_slider}
        
    def combobox_widget(self, attrib_name='', selection_list=[]):
        attrib_label = QtWidgets.QLabel(attrib_name+":")
        attrib_combobox = QtWidgets.QComboBox()
        attrib_combobox.addItems(selection_list)
        attrib_combobox.setFixedWidth(100)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addStretch()
        attrib_block.addWidget(attrib_label)
        attrib_block.addWidget(attrib_combobox)
        attrib_block.addSpacing(288)
        return {'layout_widget':attrib_block, 'label_widget':attrib_label, 'combobox_widget' : attrib_combobox}

    def checkbox_widget (self, attrib_name='', num_of_cb = 1, cb_list = []):
        attrib_checkbox = QtWidgets.QCheckBox(attrib_name)
        attrib_block = QtWidgets.QHBoxLayout()
        attrib_block.addSpacing(35)
        attrib_block.addWidget(attrib_checkbox)
        attrib_block.addStretch()
        return {'layout_widget':attrib_block, 'checkbox_widget' : attrib_checkbox}
    
    def attrib_setter(self):
        if self.selected:
            selected = self.selected[-1].fullPathName()
            if 'light' in cmds.objectType(selected).lower():
                print cmds.getAttr('%s.%s'%(selected,'intensity'))
            
            
    def maya_selection_changed(self,*args, **kwargs):
        try:
            sel = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(sel)
     
            selection_iter = om.MItSelectionList(sel)
            obj = om.MObject()
            # Loop though iterator objects
            self.selected = []
            while not selection_iter.isDone():
                # Now we can do anything with each of selected objects.
                # In this example lets just print path to iterating objects.
                selection_iter.getDependNode(obj)
                dagPath = om.MDagPath.getAPathTo(obj)
                self.selected.append(dagPath)
                selection_iter.next()
            if selection_iter.isDone():
                self.attrib_setter()
        except RuntimeError, err:
            print err    
        
    def closeEvent(self, event):        
        om.MMessage.removeCallback(self.selection_changed_callback)
        print 'closed'

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
    
