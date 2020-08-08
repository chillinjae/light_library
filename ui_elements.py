def widget_checker(self,attrib_name, value):
    if value.get('type') == 'rgb_slider':
        pass
    elif value.get('type') =='float_slider':
        return self.slider_widget(attrib_name,value)
    elif value.get('type') =='int_slider':
        return self.slider_widget(attrib_name,value)
    elif value.get('type') =='checkbox':
        return self.checkbox_widget(attrib_name,value)
    elif value.get('type') =='combobox':
        return self.combobox_widget(attrib_name,value)
    elif value.get('type') =='lineedit':
        return self.lineedit_widget(attrib_name,value)
    elif value.get('type') =='lineedit_vector':
        return self.lineedit_vector_widget(attrib_name,value)        

def slider_widget(self,attrib_name='' ,value=''):
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
        
def combobox_widget(self, attrib_name='', value=''):
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

def checkbox_widget (self, attrib_name='', num_of_cb = 1, cb_list = []):
    attrib_checkbox = QtWidgets.QCheckBox(attrib_name)
    attrib_block = QtWidgets.QHBoxLayout()
    attrib_block.addSpacing(35)
    attrib_block.addWidget(attrib_checkbox)
    attrib_block.addStretch()
    attrib_frame = QtWidgets.QFrame()
    attrib_frame.setLayout(attrib_block)
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_checkbox], 'label_widget': [], 'type': 'checkbox'}

def lineedit_widget (self, attrib_name='',value=''):
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
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit], 'label_widget': [attrib_label], 'type': 'lineedit'}

def lineedit_vector_widget (self, attrib_name='',value=''):
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
    return {'layout':attrib_frame,'label': attrib_name, 'widget' : [attrib_lineedit_x,attrib_lineedit_y,attrib_lineedit_z], 'label_widget': [attrib_label], 'type': 'lineedit_vector'}


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