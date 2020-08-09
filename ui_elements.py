from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from collections import OrderedDict 


def widget_checker(attrib_name, value):
    if value.get('type') == 'rgb_slider':
        pass
    elif value.get('type') =='float_slider':
        return slider_widget(attrib_name,value)
    elif value.get('type') =='int_slider':
        return slider_widget(attrib_name,value)
    elif value.get('type') =='checkbox':
        return checkbox_widget(attrib_name,value)
    elif value.get('type') =='combobox':
        return combobox_widget(attrib_name,value)
    elif value.get('type') =='lineedit':
        return lineedit_widget(attrib_name,value)
    elif value.get('type') =='lineedit_vector':
        return lineedit_vector_widget(attrib_name,value)        

def slider_widget(attrib_name ,value):
    attrib_label = QtWidgets.QLabel(attrib_name+":")
    attrib_value = QtWidgets.QLineEdit()
    attrib_value.setFixedWidth(80)
    attrib_value.setStyleSheet("background-color:rgb(40,40,40)")
    attrib_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    attrib_slider.setRange(value.get('range')[0],value.get('range')[1]*value.get('scale'))
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
    return {'layout':attrib_frame, 'label':attrib_name, 'widget' : [attrib_value, attrib_slider],'label_widget': [attrib_label], 'info':value, 'type': 'slider'}
        
def combobox_widget(attrib_name, value):
    attrib_label = QtWidgets.QLabel(attrib_name+":")
    attrib_combobox = QtWidgets.QComboBox()
    attrib_combobox.addItems(value.get('items'))
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
    return {'layout':attrib_frame, 'label':attrib_name, 'widget' : [attrib_combobox],'label_widget': [attrib_label], 'type': 'combobox', 'info':value}

def checkbox_widget (attrib_name,value, num_of_cb = 1, cb_list = []):
    attrib_checkbox = QtWidgets.QCheckBox(attrib_name)
    attrib_block = QtWidgets.QHBoxLayout()
    attrib_block.addSpacing(35)
    attrib_block.addWidget(attrib_checkbox)
    attrib_block.addStretch()
    attrib_frame = QtWidgets.QFrame()
    attrib_frame.setLayout(attrib_block)
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_checkbox], 'label_widget': [], 'type': 'checkbox', 'info':value}

def lineedit_widget (attrib_name,value):
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
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit], 'label_widget': [attrib_label], 'type': 'lineedit', 'info':value}

def lineedit_vector_widget (attrib_name,value):
    attrib_label = QtWidgets.QLabel(attrib_name+":")
    attrib_lineedit_x = QtWidgets.QLineEdit()
    attrib_lineedit_x.setStyleSheet("background-color:rgb(40,40,40)")
    attrib_lineedit_y = QtWidgets.QLineEdit()
    attrib_lineedit_y.setStyleSheet("background-color:rgb(40,40,40)")
    attrib_lineedit_z = QtWidgets.QLineEdit()
    attrib_lineedit_z.setStyleSheet("background-color:rgb(40,40,40)")
    attrib_block = QtWidgets.QHBoxLayout()
    attrib_block.addStretch()
    attrib_block.addWidget(attrib_label)
    attrib_block.addWidget(attrib_lineedit_x)
    attrib_block.addWidget(attrib_lineedit_y)
    attrib_block.addWidget(attrib_lineedit_z)
    attrib_block.addSpacing(80)
    attrib_frame = QtWidgets.QFrame()
    attrib_frame.setLayout(attrib_block)
    attrib_frame.setStyleSheet("background-color:rgb(80,80,80);border-radius:3px;padding:0px;margin:0px;border:0px;")
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit_x,attrib_lineedit_y,attrib_lineedit_z], 'label_widget': [attrib_label], 'type': 'lineedit_vector', 'info':value}


def set_icon_btn(label, icon=':/ambientlight.png'):
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
    
def set_attribs_to_widgets(attribs):
    widgets = OrderedDict()
    for attrib_name, value in attribs.items():
        widgets.update({attrib_name : widget_checker(value.get('name'),value)})
    return widgets
    
def set_widgets_to_group(widgets, group_name):
    group = QtWidgets.QGroupBox(group_name)
    layout = QtWidgets.QVBoxLayout()
    for attrib_name, values in widgets.items():
        if values:
            layout.addWidget(values.get('layout'))
    group.setLayout(layout)
    layout.setSpacing(2);
    return group
    
    

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
