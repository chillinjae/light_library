from collections import OrderedDict 

light_attributes = OrderedDict() 
light_visibilities = OrderedDict() 
light_transforms = OrderedDict() 
light_list = OrderedDict() 

light_attributes['decayRate']={'type':'combobox', 'items':['No Decay', 'Linear','Quadratic','Cubic'],'default':0, 'name':'Decay Rate', 'node': 'shape'}
light_attributes['aiUseColorTemperature']={'type':'checkbox','default': False, 'name':'Use Color Temperature', 'node': 'shape'}
light_attributes['color']={'type': 'rgb_slider','range':[0,1] ,'default':1, 'name':'Color', 'scale' : 1000, 'node': 'shape'}
light_attributes['intensity']={'type': 'float_slider','range':[0,10] ,'default':1, 'name':'Intensity', 'scale' : 1000, 'node': 'shape'}
light_attributes['aiColorTemperature']={'type': 'int_slider','range':[0,12000] ,'default':6500, 'name':'Temperature','scale' : 1, 'node': 'shape'}
light_attributes['aiExposure']={'type': 'float_slider','range':[-5.0,5.0] ,'default':0, 'name':'Exposure','scale' : 1000, 'node': 'shape'}
light_attributes['aiSamples']={'type': 'int_slider','range':[0,10], 'default':1, 'name':'Samples','scale' : 1, 'node': 'shape'}
light_attributes['aiRadius']={'type': 'float_slider','range':[0,100], 'default':0, 'name':'Radius','scale' : 100, 'node': 'shape'}
light_attributes['aiShadowDensity']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Shadow Intensity','scale' : 1000, 'node': 'shape'}
light_attributes['aiSpread']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Spread','scale' : 1000, 'node': 'shape'}
light_attributes['aiVolumeSamples']={'type': 'int_slider','range':[0,10] ,'default':2, 'name':'Volume Samples','scale' : 1, 'node': 'shape'}
light_attributes['aiResolution']={'type': 'lineedit','default':512, 'name':'Resolution', 'node': 'shape'}
light_attributes['emitDiffuse']={'type':'checkbox','default': True, 'name':'Emit Diffuse', 'node': 'shape'}
light_attributes['emitSpecular']={'type':'checkbox','default': True, 'name':'Emit Specular', 'node': 'shape'}
light_attributes['aiNormalize']={'type':'checkbox','default': True, 'name':'Normalize', 'node': 'shape'}
light_attributes['aiCastShadows']={'type':'checkbox','default': True, 'name':'Cast Shadows', 'node': 'shape'}
light_attributes['aiCastVolumetricShadows']={'type':'checkbox','default': True, 'name':'Cast Volumetric Shadows', 'node': 'shape'}

light_visibilities['aiDiffuse']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Diffuse', 'scale' : 1000, 'node': 'shape'}
light_visibilities['aiSpecular']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Specular', 'scale' : 1000, 'node': 'shape'}
light_visibilities['aiSss']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'SSS', 'scale' : 1000, 'node': 'shape'}
light_visibilities['aiIndirect']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Indirect', 'scale' : 1000, 'node': 'shape'}
light_visibilities['aiVolume']={'type': 'float_slider','range':[0,1] ,'default':1, 'name':'Volume', 'scale' : 1000, 'node': 'shape'}
light_visibilities['aiMaxBounces']={'type': 'lineedit','default':999, 'name':'Max Bounces', 'node': 'shape'}
light_visibilities['aiAov']={'type': 'lineedit','default':'default','name':'AOV Light Group', 'node': 'shape'}

light_transforms['translate']={'type': 'lineedit_vector','default':0, 'name':'Translate X | Y | Z', 'node': 'transform'}
light_transforms['rotate']={'type': 'lineedit_vector','default':0, 'name':'Rotate X | Y | Z', 'node': 'transform'}
light_transforms['scale']={'type': 'lineedit_vector','default':1, 'name':'Scale X | Y | Z', 'node': 'transform'}

light_list['Direct'] = {'type':'direct', 'icon':':/directionallight.png'}
light_list['Point'] = {'type':'point', 'icon':':/pointlight.png'}
light_list['Spot'] = {'type':'spot', 'icon':':/spotlight.png'}
light_list['Area'] = {'type':'area', 'icon':':/arealight.png'}


light_items = ['aiAreaLight',
             # 'aiAtmosphereVolume',
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
