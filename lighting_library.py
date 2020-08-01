import pymel.core.datatypes as dt
import maya.OpenMaya as om
import maya.cmds as cmds


cmds.selectMode(component=1)
cmds.setToolTo('Move')
pos = cmds.manipMoveContext('Move', query=True, position=True) 

selection = cmds.ls(selection=True)

vtxs = cmds.xform(selection, q=True, ws=True, t=True)
max_x = max(vtxs[0::3])
min_x = min(vtxs[0::3])
max_y = max(vtxs[1::3])
min_y = min(vtxs[1::3])
max_z = max(vtxs[2::3])
min_z = min(vtxs[2::3])

i = max_x-min_x
j = max_y-min_y
k = max_z-min_z

cmds.cmdArnoldAreaLights()
# cmds.spotLight()

target_shape = cmds.listHistory()[0]
target = cmds.listRelatives(target_shape, p=1)[0]
target = cmds.rename(target, 'test_01')

polyInfo = cmds.polyInfo(selection, fn=True)
polyInfoArray = re.findall(r"[\w.-]+", polyInfo[0]) # convert the string to array with regular expression
polyInfoX = float(polyInfoArray[2])
polyInfoY = float(polyInfoArray[3])
polyInfoZ = float(polyInfoArray[4])

cmds.move(pos[0], pos[1], pos[2], target)
angle = cmds.angleBetween( euler=True, v1=(polyInfoX, polyInfoY, polyInfoZ), v2=(i, j, k) )

constr = cmds.normalConstraint(selection, target, aimVector = (0,0,-1), worldUpType= 0)
cmds.delete(constr)

rot = cmds.getAttr(target+'.r')[0]
rot = dt.EulerRotation(*rot)
quat = rot.asQuaternion()
vecX = om.MVector(i/2,j/2,k/2)
test = vecX.rotateBy(quat)
print test.x, test.y, test.z

cmds.setAttr(target+'.s',test.x, test.y, test.z)
cmds.selectMode(object=1)