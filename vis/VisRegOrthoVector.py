#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoVector
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisRegularMesh import *


#----------------------------------------------------------------------
class VisRegOrthoVector(VisRegOrthoSlice):
    """ VisRegOrthoVectorクラス
        show orthogonal slice of regular mesh vector data 
    """

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              slicePlane =VisRegularMesh.S_Za, sliceIndex =None, useLut =True,
              showHead =True, lineWidth =1.0, minMax =None, vecScale =1.0
        """
        VisRegOrthoSlice.__init__(self, **args)
        self.showType = gfxNode.RT_WIRE
        
        self._showHead = True
        self._vecScale = 1.0
        self._useLut = True

        self._arrows = vectors.Vectors(name='OrthoVector_Arrow',
                                       localMaterial=False)
        self.addChild(self._arrows)

        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "OrthoVector"

    def setData(self, data, forceUpd=True, minmaxUpd=True):
        return VisRegularMesh.setVectorData(self, data, forceUpd, minmaxUpd)

    def setShowMode(self, showHead=True, vecScale=1.0, useLut=True,
                    forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self._showHead != showHead:
            self._showHead = showHead
            if not self._arrows is None:
                self._arrows.setHeadMode(show=showHead)
        if self._vecScale != vecScale:
            self._vecScale = vecScale
            if not self._arrows is None:
                self._arrows.setScaleFactor(vecScale)
        if self._useLut != useLut:
            self._useLut = useLut
            self._needUpdate = True
        return True

    def setBaseColor(self, color):
        """ setBaseColor -- override VisObj.setBaseColor
        """
        if self._useLut == False:
            VisObj.setBaseColor(self, color)
            return
        self._colors[0][0:3] = color[0:3]
        self.notice()
        return

    def update(self, **args):
        # check initialized
        if not self._arrows:
            return False

        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        (coord, bbox, o_p) = VisRegularMesh.getCoordArgs(self, **args)
        lut = None if not 'lut' in args else args['lut']

        slicePlane, sliceIndex = self.parseParamArgs(**args)
        
        showHead = self._showHead if not 'showHead' in args \
            else args['showHead']
        vecScale = self._vecScale if not 'vecScale' in args \
            else args['vecScale']
        useLut = True if not 'useLut' in args else args['useLut']
        lineWidth = -1.0 if not 'lineWidth' in args else args['lineWidth']

        if not data is None:
            self.setData(data, False)
        if not minmax is None:
            self.setMinMax(minmax, False)
        if not coord is None:
            self.setCoord(coord, False)
        elif not bbox is None:
            self.setCoordByBbox(bbox, False)
        elif not o_p is None:
            self.setCoordByOrgPitch(o_p, False)
        if not lut is None:
            self.lut.setTo(lut)
            self._needUpdate = True
        self.setSliceParam(slicePlane, sliceIndex, False)
        self.setShowMode(showHead, vecScale, useLut, False)
        if lineWidth > 0.0:
            self.setLineWidth(lineWidth)

        if not self._needUpdate:
            return True
        
        # update mesh coord and data
        p_data = None if self.p_data is None else self.p_data
        if self.p_coord is None or p_data is None:
            return False

        # orthogonal slice
        cslice, dslice = self.orthoSlice(p_data)

        # alloc verts and normals for _arrows
        M, N = (cslice.shape[0], cslice.shape[1])
        nv = M * N
        self._arrows.alcData(nV=nv, nN=nv)
        for j in range(N):
            for i in range(M):
                self._arrows._verts[j*M + i][:] = cslice[i, j, :]
                self._arrows._normals[j*M + i][:] = dslice[i, j, :]
        self._arrows.generateBbox()
        self._arrows.notice()

        # alloc colors for _arrows
        if self._useLut:
            self._arrows.alcData(nC=nv)
            for j in range(N):
                for i in range(M):
                    cidx = self.lut.getValIdx(np.linalg.norm(dslice[i, j]))
                    self._arrows._colors[j*M + i][:] = self.lut.entry[cidx, :]
            self._arrows.setColorMode(gfxNode.AT_PER_VERTEX)
        else:
            self._arrows._colors[0][:] = self._colors[0][:]
            self._arrows.setColorMode(gfxNode.AT_WHOLE)

        self.generateBbox()
        self._needUpdate = False
        return True

    def initPP(self):
        if self.paramsPnl is None:
            return False
        self._slicePlaneButtons = []
        
        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # slicePlane, sliceIndex, sliceIndex adjust buttons
        self.insertSlicePP(sizerTop)
        
        # showHead
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._showHeadChk = wx.CheckBox(self.paramsPnl, label='show head')
        sizerH.Add(self._showHeadChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._showHeadChk.Bind(wx.EVT_CHECKBOX, self.OnShowHeadChk)
        sizerTop.Add(wx.StaticLine(self.paramsPnl, size=wx.Size(3,3)), \
                     flag=wx.EXPAND|wx.ALL, border=0)

        # vector scale
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='vector scale'),
                   border=3)
        self._vecScaleTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                        style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._vecScaleTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._vecScaleTxt.Bind(wx.EVT_TEXT_ENTER, self.OnVecScaleTxt)

        # line width
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='line width'), border=3)
        self._lineWidthTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._lineWidthTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._lineWidthTxt.Bind(wx.EVT_TEXT_ENTER, self.OnLineWidthTxt)

        # useLut
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._useLutChk = wx.CheckBox(self.paramsPnl, label='use Lut color')
        sizerH.Add(self._useLutChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._useLutChk.Bind(wx.EVT_CHECKBOX, self.OnUseLutChk)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True

    def updatePP(self):
        if self.paramsPnl is None or \
           len(self._slicePlaneButtons) < 1 or \
           self._sliceIndexSld is None or self._sliceIndexTxt is None or \
           self._showHeadChk is None or self._vecScaleTxt is None or \
           self._useLutChk is None or self._lineWidthTxt is None:
            return False

        # slicePlane, sliceIndex
        self.updateSlicePP()

        # showHead
        self._showHeadChk.SetValue(self._showHead)

        # vector scale
        self._vecScaleTxt.SetValue(str(self._vecScale))

        # line width
        self._lineWidthTxt.SetValue(str(self.getLineWidth()))

        # useLut
        self._useLutChk.SetValue(self._useLut)

        return True

    # Event Handlers

    def OnShowHeadChk(self, event):
        val = self._showHeadChk.GetValue()
        if val == self._showHead:
            return
        if self.update(showHead=val):
            self.chkNotice()
        return

    def OnVecScaleTxt(self, event):
        try:
            val = float(self._vecScaleTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if self.update(vecScale=val):
            self.chkNotice()
        return

    def OnLineWidthTxt(self, event):
        try:
            val = float(self._lineWidthTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val <= 0.0:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val != self._lineWidth:
            self.setLineWidth(val)
            self.chkNotice()
        return

    def OnUseLutChk(self, event):
        val = self._useLutChk.GetValue()
        if val == self._useLut:
            return
        if self.update(useLut=val):
            self.chkNotice()
        return


if __name__ == '__main__':
    from pySPH import SPH
    from VisRegBounds import VisRegBounds
    import App
    app = App.GetVsnApp()
    arena = app.getArena()

    sph = SPH.SPH()
    sph.load(os.path.join("data", "uvw_010.sph"))
    gro = [sph.org[0] + sph.pitch[0]*(sph.dims[0]-1),
           sph.org[1] + sph.pitch[1]*(sph.dims[1]-1),
           sph.org[2] + sph.pitch[2]*(sph.dims[2]-1)]

    oslicer = VisRegOrthoVector(name='TestOrthoVector', data=sph.dataIndexed(),
    #                           orgPitch=[sph.org, sph.pitch])
                                bbox=[sph.org, gro])
    arena.addObject(oslicer)

    bounds = VisRegBounds(name='TestBounds', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(bounds)

    app.run(debug=True)
    
