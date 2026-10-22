#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegVolren
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from svr import *
from VisRegularMesh import *
import App


#----------------------------------------------------------------------
class VisRegVolren(VisRegularMesh):
    """ VisRegVolrenクラス
        show volume rendering of regular mesh
    """

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              minMax =None
        """
        VisRegularMesh.__init__(self, **args)

        self.p_data = None

        self._vrn = svr_node.SvrNode()
        self._vrn.Initialize()
        app = App.GetVsnApp()
        arena = app.getArena()
        arena.addVolume(self._vrn)

        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "Volren"

    def setRenderMode(self, rm):
        """ override VisObj.setRenderMode
        """
        VisObj.setRenderMode(self, rm)

        if not self._vrn is None:
            self._vrn.setRenderMode(self._renderMode)
        return

    def updateXForm(self):
        """ override VisObj.updateXForm
        """
        VisObj.updateXForm(self)

        if not self._vrn is None:
            self._vrn.setMatrix(self.getXFormMatrix())
        return

    def canLighting(self):
        """ override VisObj.canLighting
        """
        return False

    def setData(self, data, forceUpd=True, minmaxUpd=True):
        return VisRegularMesh.setScalarData(self, data, forceUpd, minmaxUpd)
        
    def update(self, **args):
        # check initialized
        if not self._vrn:
            return False

        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        (coord, bbox, o_p) = VisRegularMesh.getCoordArgs(self, **args)
        lut = None if not 'lut' in args else args['lut']

        if not minmax is None:
            self.setMinMax(minmax, False)
        elif not self.p_data is None:
            self.setMinMax([self.p_data.min(), self.p_data.max()], False)

        if not data is None:
            if self.setData(data, False):
                dims = self.p_data.shape
                dmin, dmax = (self.lut.minVal, self.lut.maxVal)
                self._vrn.SetData(self.p_data.reshape(dims[0]*dims[1]*dims[2]),
                                  dims[2], dims[1], dims[0], dmin, dmax)

        if not bbox is None:
            self.setBbox(bbox[0], bbox[1])
            self._vrn.SetGeom(bbox[0], bbox[1])
            self._vrn.updateGeom()
            self._needUpdate = True
        elif not o_p is None:
            if not self.p_data is None:
                dims = self.p_data.shape
                gro = [o_p[0][0] + o_p[1][0]*(dims[2]-1),
                       o_p[0][1] + o_p[1][1]*(dims[1]-1),
                       o_p[0][2] + o_p[1][2]*(dims[0]-1)]
                self.setBbox(o_p[0], gro)
                self._vrn.SetGeom(o_p[0], gro)
                self._vrn.updateGeom()
                self._needUpdate = True

        if not lut is None:
            self.lut.setTo(lut)
            self._vrn.SetLut(lut)
            self._needUpdate = True

        if not self._needUpdate:
            return True

        self._needUpdate = False
        return True


if __name__ == '__main__':
    from pySPH import SPH
    import App
    from VisRegBounds import VisRegBounds

    app = App.GetVsnApp()
    arena = app.getArena()

    sph = SPH.SPH()
    sph.load(os.path.join("data", "p_010.sph"))

    volren = VisRegVolren(name='TestVolren', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(volren)

    bounds = VisRegBounds(name='TestBounds', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(bounds)
    
    app.run(debug=True)
    
