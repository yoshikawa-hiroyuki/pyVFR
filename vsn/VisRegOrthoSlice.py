#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoSlice
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *


#----------------------------------------------------------------------
class VisRegOrthoSlice(VisObj):
    """ VisRegOrthoSliceクラス
        show orthogonal slice of regular mesh 
    """

    (XYP, YZP, ZXP) = range(3)

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              slicePlane =VisRegOrthoSlice.XYP, sliceIdx =None,
              showMap =True, showMeshLine =False, lineWidth =1.0, minMax =None
        """
        VisObj.__init__(self, **args)

        self.p_data = None
        self.p_coord = Node
        self._slicePlane = VisRegOrthoSlice.XYP
        self._sliceIdx = -1
        self._showMap = True
        self._showMeshLine = False
        
        self._mesh = mesh.Mesh2D(name='OrthoSlice_Mesh', localMaterial=False)
        self.addChild(self._mesh)

        data = None if not 'data' in args else args['data']
        if data:
            self.setData(data, False)

        minmax = None if not 'minMax' in args else args['minMax']
        if minMax:
            self.setMinMax(minMax, False)

        coord = None if not 'coord' in args else args['coord']
        bbox = None if not 'bbox' in args else args['bbox']
        o_p = None if not 'orgPitch' in args else args['orgPitch']
        if coord:
            self.setCoord(coord, False)
        elif bbox:
            self.setCoordByBbox(bbox, False)
        elif o_p:
            self.setCoordByOrgPitch(o_p, False)

        slicePlane, sliceIdx = -1, -1
        try:
            spl = int(args['slicePlane'])
            slicePlane = spl
        except:
            pass
        try:
            sliceIdx = int(args['sliceIdx'])
        except:
            pass
        self.setSliceParam(slicePlane, sliceIdx, False)

        showMap = True if not 'showMap' in args else args['showMap']
        showMeshLine = False if not 'showMeshLine' in args \
            else args['showMeshLine']
        self.setShowMode(showMap, showMeshLine, False)

        try:
            lw = float(args['lineWidth'])
            if lw > 0.0:
                self.setLineWidth(lw)
        except:
            pass

        if self.update(args):
            self.show = True
        return

    def setData(self, data, needUpd=True):
        if self.p_data == data:
            return True
        self.p_data = data
        if needUpd:
            return self.update()
        else:
            return True

    def setMinMax(self, minmax, needUpd=True):
        try:
            minVal = float(minmax[0])
            manVal = float(minmax[1])
        except:
            return False
        if self.lut.minVal == minVal and self.lut.maxVal == maxVal:
            return True
        if minVal > maxVal:
            bkup = minVal
            minVal = maxVal
            maxVal = bkup
        self.lut.minVal = minVal
        self.lut.maxVal = maxVal
        if needUpd:
            return self.update()
        else:
            return True

    def setCoord(self, coord, needUpd=True):
        dims = None if not self.p_data else self.p_data.shape
        try:
            cdims = coord.shape[0:3]
            if not dims:
                dims = cdims
            if cdims >= dims:
                self.p_coord = coord[:dims[0], :dims[1], :dims[2], :]
            else:
                return False
        except:
            return False
        if needUpd:
            return self.update()
        else:
            return True

    def setCoordByBbox(self, bbox, needUpd=True):
        dims = None if not self.p_data else self.p_data.shape
        if not dims: return False
        try:
            Zg, Yg, Xg = np.mgrid[
                bbox[0][0]:bbox[1][0]:complex(dims[0]),
                bbox[0][1]:bbox[1][1]:complex(dims[1]),
                bbox[0][2]:bbox[1][2]:complex(dims[2])]
            self.p_coord = np.stack([Zg, Yg, Xg], axis=-1)
        except:
            return False
        if needUpd:
            return self.update()
        else:
            return True

    def setCoordByOrgPitch(self, o_p, needUpd=True):
        dims = None if not self.p_data else self.p_data.shape
        if not dims: return False
        try:
            Zg, Yg, Xg = np.mgrid[
                o_p[0][0]:o_p[1][0]*(dims[0]-1):complex(dims[0]),
                o_p[0][1]:o_p[1][1]*(dims[1]-1):complex(dims[1]),
                o_p[0][2]:o_p[1][2]*(dims[2]-1):complex(dims[2])]
            self.p_coord = np.stack([Zg, Yg, Xg], axis=-1)
        except:
            return False
        if needUpd:
            return self.update()
        else:
            return True

    def setSliceParam(self, slicePlane=-1, sliceIdx=-1, needUpd=True):
        _needUpd = False
        if slicePlane in (VisRegOrthoSlice.XYP, VisRegOrthoSlice.YZP,
                          VisRegOrthoSlice.ZXP):
            if slicePlane != self._slicePlane:
                self._slicePlane = slicePlane
                _needUpd = True
        if sliceIdx >= 0 and self._sliceIdx != sliceIdx:
            self._sliceIdx = sliceIdx
            _needUpd = True
        if needUpd and _needUpd:
            return self.update()
        else:
            return True

    def setShowMode(self, showMap=True, showMeshLine=False, needUpd=True):
        _needUpd = False
        if self._showMap != showMap:
            self._showMap = showMap
            _needUpd = True
        if self._showMeshLine != showMeshLine:
            self._showMeshLine = showMeshLine
            _needUpd = True
        if needUpd and _needUpd:
            return self.update()
        else:
            return True


    def update(self, args):
        self.show = False
        if not self._mesh:
            return False
        if not self.p_coord:
            return False

        # update mesh coord
        dims = self.p_coord.shape
        if self._slicePlane == VisRegOrthoSlice.XYP:
            M, N, S = dims[1], dims[2], dims[0]
        elif self._slicePlane == VisRegOrthoSlice.YZP:
            M, N, S = dims[0], dims[1], dims[2]
        else: # ZXP
            M, N, S = dims[0], dims[2], dims[1]
            
        if self._sliceIdx < 0:
            self._sliceIdx = int(S / 2)
        elif self._sliceIdx >= S:
            self._sliceIdx = S -1

        if self._slicePlane == VisRegOrthoSlice.XYP:
            cslice = self.p_coord[self._sliceIdx, :, :, :]
            if self.p_data:
                dslice = self.p_data[self._sliceIdx, :, :]
        elif self._slicePlane == VisRegOrthoSlice.YZP:
            cslice = self.p_coord[:, :, self._sliceIdx, :]
            if self.p_data:
                dslice = self.p_data[:, :, self._sliceIdx]
        else: # ZXP
            cslice = self.p_coord[:, self._sliceIdx, :, :]
            if self.p_data:
                dslice = self.p_data[:, self._sliceIdx, :]

        self._mesh.setMeshSize(M, N)
        for j in range(N):
            for i in range(M):
                self._mesh._verts[j*M + i][:] = cslice[i, j, :]
        if self.p_data:
            self._mesh.alcData(nC=self._mesh.getNumVerts())
            for j in range(N):
                for i in range(M):
                    cidx = self.lut.getValIdx(dslice[i, j])
                    self._mesh._colors[:] = self._lut.entry[cidx, :]

        if self._showMeshLine:
            self.showType = gfxNode.RT_WIRE
            self._mesh.setAuxLineColor(True. self._colors[0])
        if self._showMap and self.p_data:
            self.showType += gfxNode.RT_SMOOTH

        return True
    
