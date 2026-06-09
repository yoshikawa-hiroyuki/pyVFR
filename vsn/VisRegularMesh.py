#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegularMesh
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *


#----------------------------------------------------------------------
class VisRegularMesh(VisObj):
    """ VisRegularMeshクラス
        Base class of VisObj for regular mesh
    """

    def __init__(self, **args):
        VisObj.__init__(self, **args)
        
        self._needUpdate = False
        self.p_coord = None
        return

    def getCoordArgs(self, **args):
        """
        args: coord =None, bbox =None, orgPitch =None
        """
        coord = None if not 'coord' in args else args['coord']
        bbox = None if not 'bbox' in args else args['bbox']
        orgPitch = None if not 'orgPitch' in args else args['orgPitch']
        return (coord, bbox, orgPitch)

    def setCoord(self, coord, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        dims = None if self.p_data is None else self.p_data.shape[0:3]
        try:
            cdims = coord.shape[0:3]
            if not dims:
                dims = cdims
            if cdims >= dims:
                self.p_coord = coord[:dims[0], :dims[1], :dims[2], :]
                self._needUpdate = True
            else:
                return False
        except:
            return False
        return True

    def setCoordByBbox(self, bbox, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        dims = None if self.p_data is None else self.p_data.shape
        if not dims: return False
        try:
            Zg, Yg, Xg = np.mgrid[
                bbox[0][2]:bbox[1][2]:complex(dims[0]),
                bbox[0][1]:bbox[1][1]:complex(dims[1]),
                bbox[0][0]:bbox[1][0]:complex(dims[2])]
            self.p_coord = np.stack([Xg, Yg, Zg], axis=-1)
            self._needUpdate = True
        except:
            return False
        return True

    def setCoordByOrgPitch(self, o_p, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        dims = None if self.p_data is None else self.p_data.shape
        if dims is None:
            return False
        try:
            gro = [o_p[0][0] + o_p[1][0]*(dims[2]-1),
                   o_p[0][1] + o_p[1][1]*(dims[1]-1),
                   o_p[0][2] + o_p[1][2]*(dims[0]-1)]
            Zg, Yg, Xg = np.mgrid[
                o_p[0][2]:gro[2]:complex(dims[0]),
                o_p[0][1]:gro[1]:complex(dims[1]),
                o_p[0][0]:gro[0]:complex(dims[2])]
            self.p_coord = np.stack([Xg, Yg, Zg], axis=-1)
            self._needUpdate = True
        except:
            return False
        return True

