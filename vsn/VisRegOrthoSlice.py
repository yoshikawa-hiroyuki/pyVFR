#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoSlice
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *


#----------------------------------------------------------------------
class VisRegOrthoSlice(VisObj):
    """ VisRegOrthoSliceクラス
        show orthogonal slice of regular mesh 
    """

    (S_Za, S_Ya, S_Xa) = range(3)

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              slicePlane =VisRegOrthoSlice.S_Za, sliceIndex =None,
              showMap =True, showMeshLine =False, lineWidth =1.0, minMax =None
        """
        VisObj.__init__(self, **args)

        self._needUpdate = False
        self.p_data = None
        self.p_coord = None
        self._slicePlane = VisRegOrthoSlice.S_Za
        self._sliceIndex = -1
        self._showMap = True
        self._showMeshLine = False
        
        self._mesh = mesh.Mesh2D(name='OrthoSlice_Mesh', localMaterial=False)
        self._mesh.setNormalMode(gfxNode.AT_PER_FACE)
        self._mesh.setColorMode(gfxNode.AT_PER_VERTEX)
        self.addChild(self._mesh)

        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "OrthoSlice"

    def setData(self, data, forceUpd=True, minmaxUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self.p_data is data:
            return True
        if isinstance(data, np.ndarray) and len(data.shape) >= 3:
            if len(data.shape) > 3:
                self.p_data = data[:, :, :, 0]
            else:
                self.p_data = data
            if minmaxUpd:
                self.setMinMax([self.p_data.min(), self.p_data.max()])
        else:
            return False
        self._needUpdate = True
        return True

    def setMinMax(self, minmax, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        try:
            minVal = float(minmax[0])
            maxVal = float(minmax[1])
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
        self.updateUI()
        self._needUpdate = True
        return True

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

    def setSliceParam(self, slicePlane=-1, sliceIndex=-1, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if slicePlane in (VisRegOrthoSlice.S_Za, VisRegOrthoSlice.S_Xa,
                          VisRegOrthoSlice.S_Ya):
            if slicePlane != self._slicePlane:
                self._slicePlane = slicePlane
                self._needUpdate = True
        if sliceIndex >= 0 and self._sliceIndex != sliceIndex:
            self._sliceIndex = sliceIndex
            self._needUpdate = True
        return True

    def setShowMode(self, showMap=True, showMeshLine=False, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self._showMap != showMap:
            self._showMap = showMap
            self._needUpdate = True
        if self._showMeshLine != showMeshLine:
            self._showMeshLine = showMeshLine
            self._needUpdate = True
        return True

    def setBaseColor(self, color):
        """ setBaseColor -- override VisObj.setRenderMode
        """
        self._colors[0][0:3] = color[0:3]
        self.notice()
        return

    def update(self, **args):
        # check initialized
        if not self._mesh:
            return False

        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        coord = None if not 'coord' in args else args['coord']
        bbox = None if not 'bbox' in args else args['bbox']
        o_p = None if not 'orgPitch' in args else args['orgPitch']
        lut = None if not 'lut' in args else args['lut']

        slicePlane = -1 if not 'slicePlane' in args else args['slicePlane']
        sliceIndex = -1 if not 'sliceIndex' in args else args['sliceIndex']
        showMap = self._showMap if not 'showMap' in args else args['showMap']
        showMeshLine = self._showMeshLine if not 'showMeshLine' in args \
            else args['showMeshLine']
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
        self.setShowMode(showMap, showMeshLine, False)
        if lineWidth > 0.0:
            self.setLineWidth(lineWidth)

        if not self._needUpdate:
            return True
        
        # update mesh coord and data
        p_data = None if self.p_data is None else self.p_data

        if self.p_coord is None:
            return False

        dims = self.p_coord.shape
        if self._slicePlane == VisRegOrthoSlice.S_Za:
            S = dims[0]
        elif self._slicePlane == VisRegOrthoSlice.S_Xa:
            S = dims[2]
        else: # S_Ya
            S = dims[1]
        if self._sliceIndex < 0:
            self._sliceIndex = int(S / 2)
        elif self._sliceIndex >= S:
            self._sliceIndex = S -1
            
        if self._slicePlane == VisRegOrthoSlice.S_Za:
            cslice = self.p_coord[self._sliceIndex, :, :, :]
            if not p_data is None:
                dslice = p_data[self._sliceIndex, :, :]
        elif self._slicePlane == VisRegOrthoSlice.S_Xa:
            cslice = self.p_coord[:, :, self._sliceIndex, :]
            if not p_data is None:
                dslice = p_data[:, :, self._sliceIndex]
        else: # S_Ya
            cslice = self.p_coord[:, self._sliceIndex, :, :]
            if not p_data is None:
                dslice = p_data[:, self._sliceIndex, :]

        M, N = (cslice.shape[0], cslice.shape[1])
        self._mesh.setMeshSize(M, N)
        for j in range(N):
            for i in range(M):
                self._mesh._verts[j*M + i][:] = cslice[i, j, :]
        self._mesh.generateBbox()
        self._mesh.generateNormals()
        if not p_data is None:
            self._mesh.alcData(nC=self._mesh.getNumVerts())
            for j in range(N):
                for i in range(M):
                    cidx = self.lut.getValIdx(dslice[i, j])
                    self._mesh._colors[j*M + i][:] = self.lut.entry[cidx, :]
                    continue # for i
                continue # for j
            
        # update mesh show mode
        showType = gfxNode.RT_NONE
        if self._showMeshLine:
            showType = gfxNode.RT_WIRE
            self._mesh.setAuxLineColor(True, self._colors[0])
        if self._showMap and not p_data is None:
            showType += gfxNode.RT_SMOOTH
        self._mesh.setRenderMode(showType)

        self.generateBbox()
        self._needUpdate = False
        return True
    
    def initPP(self):
        if self.paramsPnl is None:
            return False
        self._slicePlaneButtons = []

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # slicePlane
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='slice plane'))
        choices = ["XY", "XZ", "YZ"]
        for i, choice in enumerate(choices):
            style = wx.RB_GROUP if i == 0 else 0
            rb = wx.RadioButton(self.paramsPnl, label=choice, style=style)
            rb.Bind(wx.EVT_RADIOBUTTON, self.OnSlicePlaneRadio)
            sizerH.Add(rb, flag=wx.ALL, border=3)
            self._slicePlaneButtons.append(rb)
            continue # for i,choice
        
        # sliceIndex
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._sliceIndexSld = wx.Slider(self.paramsPnl,
                                        style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        sizerH.Add(self._sliceIndexSld, flag=wx.EXPAND|wx.ALL, \
                   proportion=1, border=3)
        self._sliceIndexSld.Bind(wx.EVT_SLIDER, self.OnSliceIndexSld)
        self._sliceIndexTxt = wx.TextCtrl(self.paramsPnl, value='', \
                                          size=wx.Size(50,-1), \
                                          style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._sliceIndexTxt, flag=wx.EXPAND|wx.ALL, border=3)
        self._sliceIndexTxt.Bind(wx.EVT_TEXT_ENTER, self.OnSliceIndexTxt)

        # sliceIndex adjust buttons
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._sliceMinusBtn = wx.Button(self.paramsPnl, label='<', \
                                        style=wx.BU_EXACTFIT)
        sizerH.Add(self._sliceMinusBtn, flag=wx.EXPAND|wx.ALL, border=3)
        self._sliceMinusBtn.Bind(wx.EVT_BUTTON, self.OnSliceMinusBtn)
        self._slicePlusBtn = wx.Button(self.paramsPnl, label='>', \
                                       style=wx.BU_EXACTFIT)
        sizerH.Add(self._slicePlusBtn, flag=wx.EXPAND|wx.ALL, border=3)
        self._slicePlusBtn.Bind(wx.EVT_BUTTON, self.OnSlicePlusBtn)
        sizerTop.Add(wx.StaticLine(self.paramsPnl, size=wx.Size(3,3)), \
                     flag=wx.EXPAND|wx.ALL, border=0)
        
        # showMap
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._showMapChk = wx.CheckBox(self.paramsPnl, label='show map')
        sizerH.Add(self._showMapChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._showMapChk.Bind(wx.EVT_CHECKBOX, self.OnShowMapChk)
        sizerTop.Add(wx.StaticLine(self.paramsPnl, size=wx.Size(3,3)), \
                     flag=wx.EXPAND|wx.ALL, border=0)

        # showMeshLine
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._showMeshLineChk = wx.CheckBox(self.paramsPnl, \
                                            label='show mesh line')
        sizerH.Add(self._showMeshLineChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._showMeshLineChk.Bind(wx.EVT_CHECKBOX, self.OnShowMeshLineChk)

        # line_width
        sizerH.Add(wx.StaticText(self.paramsPnl, label=' width'), border=3)
        self._lineWidthTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._lineWidthTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._lineWidthTxt.Bind(wx.EVT_TEXT_ENTER, self.OnLineWidthTxt)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True
    
    def updatePP(self):
        if self.paramsPnl is None or \
           len(self._slicePlaneButtons) < 1 or \
           self._sliceIndexSld is None or self._sliceIndexTxt is None or \
           self._showMapChk is None or \
           self._showMeshLineChk is None or self._lineWidthTxt is None:
            return False

        # slicePlane
        if self._slicePlane == VisRegOrthoSlice.S_Ya:
            self._slicePlaneButtons[VisRegOrthoSlice.S_Ya].SetValue(True)
        elif self._slicePlane == VisRegOrthoSlice.S_Xa:
            self._slicePlaneButtons[VisRegOrthoSlice.S_Xa].SetValue(True)
        else:
            self._slicePlaneButtons[VisRegOrthoSlice.S_Za].SetValue(True)
        
        # sliceIndex
        if not self.p_data is None and len(self.p_data.shape) == 3:
            self._sliceIndexSld.SetRange(0, self.p_data.shape[self._slicePlane])
            if self._sliceIndex < 0:
                self._sliceIndex = int(self.p_data.shape[self._slicePlane]/2)
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))

        # showMap
        self._showMapChk.SetValue(self._showMap)

        # showMeshLine
        self._showMeshLineChk.SetValue(self._showMeshLine)

        # line_width
        self._lineWidthTxt.SetValue(str(self.getLineWidth()))

        return True

    # Event Handlers

    def OnSlicePlaneRadio(self, event):
        if self.p_data is None or len(self.p_data.shape) != 3:
            return
        new_sliceAxs = None
        if self._slicePlaneButtons[VisRegOrthoSlice.S_Za].GetValue() == True:
            new_sliceAxs = VisRegOrthoSlice.S_Za
        elif self._slicePlaneButtons[VisRegOrthoSlice.S_Ya].GetValue() == True:
            new_sliceAxs = VisRegOrthoSlice.S_Ya
        elif self._slicePlaneButtons[VisRegOrthoSlice.S_Xa].GetValue() == True:
            new_sliceAxs = VisRegOrthoSlice.S_Xa
        if new_sliceAxs is None:
            new_sliceAxs = VisRegOrthoSlice.S_Za
            self._slicePlaneButtons[VisRegOrthoSlice.S_Za].GetValue(True)
        if self._slicePlane == new_sliceAxs:
            return
        
        if self.setSliceParam(slicePlane=new_sliceAxs):
            self._sliceIndexSld.SetRange(0, self.p_data.shape[self._slicePlane])
            if self.update():
                self.chkNotice()
        return

    def OnSliceIndexSld(self, event):
        if self.p_data is None or len(self.p_data.shape) != 3:
            return
        val = self._sliceIndexSld.GetValue()
        if val == self._sliceIndex:
            return
        if self.setSliceParam(sliceIndex=val):
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            if self.update():
                self.chkNotice()
        return

    def OnSliceIndexTxt(self, event):
        if self.p_data is None or len(self.p_data.shape) != 3:
            return
        try:
            val = int(self._sliceIndexTxt.GetValue())
        except:
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            return
        if val == self._sliceIndex:
            return
        if self.setSliceParam(sliceIndex=val):
            self._sliceIndexSld.SetValue(self._sliceIndex)
            if self.update():
                self.chkNotice()
        return

    def OnSliceMinusBtn(self, event):
        if self.p_data is None or len(self.p_data.shape) != 3:
            return
        if self.setSliceParam(sliceIndex=self._sliceIndex -1):
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            if self.update():
                self.chkNotice()
        return

    def OnSlicePlusBtn(self, event):
        if self.p_data is None or len(self.p_data.shape) != 3:
            return
        if self.setSliceParam(sliceIndex=self._sliceIndex +1):
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            if self.update():
                self.chkNotice()
        return

    def OnShowMapChk(self, event):
        val = self._showMapChk.GetValue()
        if val == self._showMap:
            return
        if self.update(showMap=val):
            self.chkNotice()
        return

    def OnShowMeshLineChk(self, event):
        val = self._showMeshLineChk.GetValue()
        if val == self._showMeshLine:
            return
        if self.update(showMeshLine=val):
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
    
    files = [f"p_{i:03d}.sph" for i in range(1, 11)]
    sph = SPH.SPH()
    sph.load(os.path.join("data", files[-1]))
    print(f"dims={sph.dims}")
    print(f"org={sph.org}")
    print(f"pitch={sph.pitch}")
    gro = [sph.org[0] + sph.pitch[0]*(sph.dims[0]-1),
           sph.org[1] + sph.pitch[1]*(sph.dims[1]-1),
           sph.org[2] + sph.pitch[2]*(sph.dims[2]-1)]
    print(f"gro={gro}")

    oslicer = VisRegOrthoSlice(name='TestOrthoSlice', data=sph.dataIndexed(),
    #                           orgPitch=[sph.org, sph.pitch])
                               bbox=[sph.org, gro])
    arena.addObject(oslicer)

    bounds = VisRegBounds(name='TestBounds', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(bounds)

    #app.run_console()
    app.run(debug=True)
