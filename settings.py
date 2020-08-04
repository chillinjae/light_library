light_attributes = {
    'color':{'type': 'rgb_slider','range':[0,1] ,'default':1}
    ,'intensity':{'type': 'float_slider','range':[0,10] ,'default':1}
    ,'emitDiffuse':{'type':'checkbox','default': True}
    ,'emitSpecular':{'type':'checkbox','default': True}
    ,'decayRate':{'type':'combobox', 'items':['No Decay', 'Linear','Quadratic','Cubic'],'default':0}
    ,'aiUseColorTemperature':{'type':'checkbox','default': False}
    ,'aiColorTemperature':{'type': 'int_slider','range':[0,12000] ,'default':6500}
    ,'aiExposure':{'type': 'float_slider','range':[-5.0,5.0] ,'default':0}
    ,'aiSamples':{'type': 'int_slider','range':[0,10], 'default':1}
    ,'aiRadius':{'type': 'float_slider','range':[0,10], 'default':0}
    ,'aiNormalize':{'type':'checkbox','default': True}
    ,'aiCastShadows':{'type':'checkbox','default': True}
    ,'aiShadowDensity':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiResolution':{'type': 'lineedit','default':512}
    ,'aiSpread':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiVolumeSamples':{'type': 'int_slider','range':[0,10] ,'default':2}
    ,'aiCastVolumetricShadows':{'type':'checkbox','default': True}

    ,'aiDiffuse':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiSpecular':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiSss':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiIndirect':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiVolume':{'type': 'float_slider','range':[0,1] ,'default':1}
    ,'aiMaxBounces':{'type': 'lineedit','default':999}
    ,'aiAov':{'type': 'lineedit','default':'default'},
    'translate':{'type': 'lineedit','default':0},
    'translateX':{'type': 'lineedit','default':0},
    'translateY':{'type': 'lineedit','default':0},
    'translateZ':{'type': 'lineedit','default':0},
    'rotate':{'type': 'lineedit','default':0},
    'rotateX':{'type': 'lineedit','default':0},
    'rotateY':{'type': 'lineedit','default':0},
    'rotateZ':{'type': 'lineedit','default':0},
    'scale':{'type': 'lineedit','default':1},
    'scaleX':{'type': 'lineedit','default':1},
    'scaleY':{'type': 'lineedit','default':1},
    'scaleZ':{'type': 'lineedit','default':1},
}
