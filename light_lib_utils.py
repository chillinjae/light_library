import sys
import pymel.core.datatypes as dt
import maya.OpenMaya as om
import maya.cmds as cmds
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

setting_path = 'C:/Users/jaec/PycharmProjects/light_library/light_library'
sys.path.append(setting_path)
sys.dont_write_bytecode=True

import settings 
reload(settings)
from settings import light_items

def light_selected(list_widget,selected):
    list_widget.clearSelection()
    update_light_list(list_widget)
    if selected:
        for sel in selected:
            try:
                list_widget.findItems(sel.fullPathName(),QtCore.Qt.MatchExactly)[0].setSelected(1)
            except:
                pass

def get_scene_lights():
    lights = []
    for light in light_items:
        lights+=cmds.ls(type=[light],l=1)
    lights = sorted(list(set(lights)))
    return lights
    
def set_light(light_type, list_widget, *args):
    selection = cmds.ls(sl=1)
    if selection:
        if cmds.objectType(selection[0]) == 'transform':
            [create_light_by_location(light_type, selected, 'transform') for selected in selection]
        elif cmds.objectType(selection[0]) == 'mesh':
            create_light_by_location(light_type, selection, 'mesh')
    update_light_list(list_widget)

def create_light_by_location(light_type, selected, obj_type):
    cmds.select(selected)
    selection = cmds.ls(sl=1)
    selection = cmds.polyListComponentConversion( selection, tf=True )
    cmds.select(selection)
    selection = cmds.ls(sl=1)
    cmds.selectMode(component=1)
    cmds.selectPref(useDepth=1)
    cmds.setToolTo('Move')
    pos = cmds.manipMoveContext('Move', query=True, position=True) 
    current_lights = get_scene_lights()
    create_light(light_type)        
    added_lights = get_scene_lights()
    target_shape = list(set(added_lights) - set(current_lights))[0]
    target = cmds.listRelatives(target_shape, p=1)[0]
    if obj_type == 'mesh':
        vtxs = cmds.xform(selection, q=True, ws=True, t=True)
        vectors = [om.MVector(*vtxs[i:i + 3]) for i in range(0, len(vtxs), 3)]
        vectors_left = [om.MVector(*vtxs[i:i + 3]) for i in range(0, len(vtxs), 3)]
        start_vec_idx, end_vec_idx = longest_length(vectors)
        start_vec = vectors[start_vec_idx]
        end_vec = vectors[end_vec_idx]
        mid_vec_idx = farest_vector(start_vec, end_vec, vectors)
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
    
def longest_length(vectors):
    max_length = [0,0,0]
    for i in range(len(vectors)-1):
        for j in range(i,len(vectors)):
            length = (vectors[i]-vectors[j]).length()
            if length > max_length[0]:
                max_length = [length, i, j]
    return max_length[1], max_length[2]

def farest_vector(start_vec, end_vec, vectors):
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

def create_light(light_type):
    if light_type == 'area':
        cmds.cmdArnoldAreaLights()
    elif light_type == 'spot':
        cmds.spotLight()
    elif light_type == 'point':
        cmds.pointLight()
    elif light_type == 'direct':
        return 0 

def select_light(list_widget):
    cmds.select([selected.text() for selected in list_widget.selectedItems()])

def update_light_list(list_widget):
    current_lights = get_scene_lights()
    scene_lights = get_all_items_by_name(list_widget)
    if current_lights == scene_lights:
        return 0
    else:
        added = list(set(current_lights) - set(scene_lights))
        deleted = list(set(scene_lights) - set(current_lights))
    [list_widget.takeItem(list_widget.row(list_widget.findItems(d,QtCore.Qt.MatchExactly)[0])) for d in deleted]
    list_widget.addItems(added)
    scene_lights = current_lights

def get_all_items(list_widget):
    items = []
    for index in range(list_widget.count()):
        items.append(list_widget.item(index))
    return items

def get_all_items_by_name(list_widget):
    return [item.text() for item in get_all_items(list_widget)]
    




        
