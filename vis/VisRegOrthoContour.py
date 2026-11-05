#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoContour
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisRegularMesh import *


#----------------------------------------------------------------------
class VisRegOrthoContour(VisRegOrthoSlice):
    """ VisRegOrthoContourクラス
        show contour lines on orthogonal slice of regular mesh scalar data 
    """

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              slicePlane =VisRegOrthoSlice.S_Za, sliceIndex =None,
              numLines =5, lineWidth =1.0, useLut =True, minMax =None
        """
        VisRegOrthoSlice.__init__(self, **args)
        self.showType = gfxNode.RT_WIRE
        
        self._numLines = 5
        self._useLut = True
        
        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "OrthoContour"

    def setData(self, data, forceUpd=True, minmaxUpd=True):
        return VisRegularMesh.setScalarData(self, data, forceUpd, minmaxUpd)
        
    def setNumLines(self, numLines, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if numLines > 0:
            if self._numLines != numLines:
                self._numLines = numLines
                self._needUpdate = True
            return True
        return False
    
    def setUseLut(self, useLut=True, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self._useLut != useLut:
            self._useLut = useLut
            self._needUpdate = True
        return True

    def calcLineSeg(self, p0, p1, p2, val0, val1, val2, val, lp1, lp2):
        vFlg = [0, 0, 0]
        j = 0
        if val0 > val: vFlg[0] = 1; j += 1
        if val1 > val: vFlg[1] = 1; j += 1
        if val2 > val: vFlg[2] = 1; j += 1
        if j == 0 or j == 3: return False

        pos = [p0, p1, p2]
        vals = [val0, val1, val2]
        top = -1; bot = [-1, -1]
        if j == 1:
            idx = 0
            for i in range(3):
                if vFlg[i] == 1: top = i
                else: bot[idx] = i; idx += 1
        else:
            idx = 0
            for i in range(3):
                if vFlg[i] == 0: top = i
                else: bot[idx] = i; idx += 1

        # lp1: top---bot[0]
        if vals[top] == vals[bot[0]]: return False
        t = (val - vals[top]) / (vals[bot[0]] - vals[top])
        lp = pos[top] + (pos[bot[0]] - pos[top]) * t
        lp1[0] = lp[0]; lp1[1] = lp[1]; lp1[2] = lp[2]

        # lp2 : top---bot[1]
        if vals[top] == vals[bot[1]]: return False
        t = (val - vals[top]) / (vals[bot[1]] - vals[top])
        lp = pos[top] + (pos[bot[1]] - pos[top]) * t
        lp2[0] = lp[0]; lp2[1] = lp[1]; lp2[2] = lp[2]

        return True
        
    def update(self, **args):
        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        (coord, bbox, o_p) = VisRegularMesh.getCoordArgs(self, **args)
        lut = None if not 'lut' in args else args['lut']

        slicePlane, sliceIndex = self.parseParamArgs(**args)
        
        numLines = self._numLines if not 'numLines' in args \
            else args['numLines']
        useLut = self._useLut if not 'useLut' in args else args['useLut']
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

        self.setNumLines(numLines, False)
        self.setUseLut(useLut, False)

        if lineWidth > 0.0:
            self.setLineWidth(lineWidth)

        if not self._needUpdate:
            return True
        self.remAllChildren()
        if self._numLines < 1:
            return True
        
        # update coord and data
        p_data = None if self.p_data is None else self.p_data
        if self.p_coord is None:
            return False

        # orthogonal slice
        cslice, dslice = self.orthoSlice(p_data)

        M, N = (cslice.shape[0], cslice.shape[1])
        dv = 0.0 if self._numLines < 2 else \
            (self.lut.maxVal - self.lut.minVal) / (self._numLines -1)

        # lines loop
        vv = np.zeros(5)
        vc = np.zeros(3, dtype=np.float32)
        lp1 = np.zeros(3, dtype=np.float32); lp2 = np.zeros(3, dtype=np.float32)
        val = self.lut.minVal
        for l in range(self._numLines):
            # allocate lines
            lns = lines.Lines(name='RegOrthoContour_Lines', localMaterial=False)
            self.addChild(lns)

            # count valid cells
            cnt_vc = 0
            for j in range(N-1):
                for i in range(M-1):
                    vflgs = np.zeros(5, dtype=np.int8)
                    vv[0] = dslice[i  , j  ]
                    vv[1] = dslice[i+1, j  ]
                    vv[2] = dslice[i+1, j+1]
                    vv[3] = dslice[i  , j+1]
                    vv[4] = (vv[0] + vv[1] + vv[2] +vv[3]) * 0.25
                    for k in range(5):
                        if vv[k] > val: vflgs[k] = 1
                    for vidxs in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
                        vfSum = vflgs[vidxs[0]]+vflgs[vidxs[1]]+vflgs[vidxs[2]]
                        if vfSum == 1 or vfSum == 2:
                            cnt_vc += 1
                    continue # end of for(i)
                continue # end of for(j)
            if cnt_vc < 1:
                val += dv
                continue
            lns.alcData(nV=cnt_vc*2)

            idx = 0
            for j in range(N-1):
                for i in range(M-1):
                    vv[0] = dslice[i  , j  ]
                    vv[1] = dslice[i+1, j  ]
                    vv[2] = dslice[i+1, j+1]
                    vv[3] = dslice[i  , j+1]
                    vv[4] = (vv[0] + vv[1] + vv[2] +vv[3]) * 0.25
                        
                    vc[0] = (cslice[i  , j  , 0] + cslice[i+1, j  , 0] + \
                             cslice[i+1, j+1, 0] + cslice[i  , j+1, 0]) * 0.25
                    vc[1] = (cslice[i  , j  , 1] + cslice[i+1, j  , 1] + \
                             cslice[i+1, j+1, 1] + cslice[i  , j+1, 1]) * 0.25
                    vc[2] = (cslice[i  , j  , 2] + cslice[i+1, j  , 2] + \
                             cslice[i+1, j+1, 2] + cslice[i  , j+1, 2]) * 0.25
                        
                    # triangle(0, 1, C)
                    if self.calcLineSeg(cslice[i,j,:], cslice[i+1,j,:], vc,
                                        vv[0], vv[1], vv[4], val, lp1, lp2):
                        lns._verts[idx][:] = lp1[:]; idx += 1
                        lns._verts[idx][:] = lp2[:]; idx += 1
                    # triangle(1, 2, C)
                    if self.calcLineSeg(cslice[i+1,j,:], cslice[i+1,j+1,:], vc,
                                        vv[1], vv[2], vv[4], val, lp1, lp2):
                        lns._verts[idx][:] = lp1[:]; idx += 1
                        lns._verts[idx][:] = lp2[:]; idx += 1
                    # triangle(2, 3, C)
                    if self.calcLineSeg(cslice[i+1,j+1,:], cslice[i,j+1,:], vc,
                                        vv[2], vv[3], vv[4], val, lp1, lp2):
                        lns._verts[idx][:] = lp1[:]; idx += 1
                        lns._verts[idx][:] = lp2[:]; idx += 1
                    # triangle(3, 0, C)
                    if self.calcLineSeg(cslice[i,j+1,:], cslice[i,j,:], vc,
                                        vv[3], vv[0], vv[4], val, lp1, lp2):
                        lns._verts[idx][:] = lp1[:]; idx += 1
                        lns._verts[idx][:] = lp2[:]; idx += 1
                    continue # end of for(i)
                continue # end of for(j)

            # lines' attr
            lns.generateBbox()
            if self._useLut:
                cidx = self.lut.getValIdx(val)
                lns._colors[0][:] = self.lut.entry[cidx, :]
            else:
                lns._colors[0][:] = self._colors[0][:]

            val += dv
            continue # end of for(j)

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
        
        # numLines
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='#of lines'), border=3)
        self._numLinesTxt = wx.TextCtrl(self.paramsPnl, value='5', \
                                        style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._numLinesTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._numLinesTxt.Bind(wx.EVT_TEXT_ENTER, self.OnNumLinesTxt)

        # lineWidth
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
        self._useLutChk = wx.CheckBox(self.paramsPnl, label='use cmap')
        sizerH.Add(self._useLutChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._useLutChk.Bind(wx.EVT_CHECKBOX, self.OnUseLutChk)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True
    
    def updatePP(self):
        if self.paramsPnl is None:
            return False

        # slicePlane, sliceIndex
        self.updateSlicePP()

        # numLines
        self._numLinesTxt.SetValue(str(self._numLines))

        # lineWidth
        self._lineWidthTxt.SetValue(str(self.getLineWidth()))

        # useLut
        self._useLutChk.SetValue(self._useLut)

        return True

    # Event Handlers

    def OnUseLutChk(self, event):
        val = self._useLutChk.GetValue()
        if val == self._useLut:
            return
        if self.update(useLut=val):
            self.chkNotice()
        return

    def OnNumLinesTxt(self, event):
        try:
            val = int(self._numLinesTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val < 1:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val == self._numLines:
            return
        if self.update(numLines=val):
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
    

if __name__ == '__main__':
    from pySPH import SPH
    from VisRegBounds import VisRegBounds
    import App
    app = App.GetVsnApp()
    arena = app.getArena()
    
    sph = SPH.SPH()
    sph.load(os.path.join("data", "p_010.sph"))
    print(f"dims={sph.dims}")
    print(f"org={sph.org}")
    print(f"pitch={sph.pitch}")
    gro = [sph.org[0] + sph.pitch[0]*(sph.dims[0]-1),
           sph.org[1] + sph.pitch[1]*(sph.dims[1]-1),
           sph.org[2] + sph.pitch[2]*(sph.dims[2]-1)]
    print(f"gro={gro}")

    oslicer = VisRegOrthoContour(name='TestOrthoContour',data=sph.dataIndexed(),
    #                           orgPitch=[sph.org, sph.pitch])
                                bbox=[sph.org, gro])
    arena.addObject(oslicer)

    bounds = VisRegBounds(name='TestBounds', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(bounds)

    #app.run_console()
    app.run(debug=True)
