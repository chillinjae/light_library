import pymel.core.datatypes as dt
import maya.OpenMaya as om
import maya.cmds as cmds

def longest_length(vectors):
    max_length = [0,0,0]
    for i in range(len(vectors)-1):
        for j in range(i,len(vectors)):
            length = (vectors[i]-vectors[j]).length()
            print length,i ,j
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
        print [result, i]
        if result > farest_vec[0]:
            farest_vec = [result, i]
    return farest_vec[1]
    
def create_light(light_type):
    cmds.selectMode(component=1)
    cmds.setToolTo('Move')
    pos = cmds.manipMoveContext('Move', query=True, position=True) 

    selection = cmds.ls(selection=True)

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
    
    cmds.spaceLocator(p=(start_vec.x,start_vec.y,start_vec.z))
    cmds.spaceLocator(p=(end_vec.x,end_vec.y,end_vec.z))
    cmds.spaceLocator(p=(mid_vec.x,mid_vec.y,mid_vec.z))

    if light_type == 'area':
        cmds.cmdArnoldAreaLights()
    elif light_type == 'spot':
        cmds.spotLight()

    target_shape = cmds.listHistory()[0]
    target = cmds.listRelatives(target_shape, p=1)[0]

    cmds.move(pos[0], pos[1], pos[2], target)

    constr = cmds.normalConstraint(selection, target, aimVector = (0,0,-1), wu = (up_vec.x,up_vec.y,up_vec.z), worldUpType= 2)
    cmds.delete(constr)

    cmds.setAttr(target+'.s',edge_vec_01.length()/2, edge_vec_02.length()/2, edge_vec_02.length()/2)
    select_tool = cmds.selectContext('Select Tool')
    cmds.setToolTo(select_tool)
    cmds.selectMode(object=1, component=False)

def area(*args):
    create_light('area')

def spot(*args):
    create_light("spot")

def point(*args):
    pass
    
cmds.window( width=150 )
cmds.columnLayout( adjustableColumn=True )
cmds.button( label='ai area light', command=area )
cmds.button( label='spot light', align='left', command=spot)
cmds.button( label='spot light', align='left', command=point)
cmds.showWindow()


