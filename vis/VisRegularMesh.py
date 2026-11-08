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
        self.p_data = None
        self.p_coord = None
        return

    def setScalarData(self, data, forceUpd=True, minmaxUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self.p_data is data:
            return True
        if isinstance(data, np.ndarray) and len(data.shape) in (3, 4):
            if len(data.shape) == 4:
                self.p_data = data[:, :, :, 0].astype(np.float32, copy=False)
            else:
                self.p_data = data.astype(np.float32, copy=False)
            if minmaxUpd:
                self.setMinMax([self.p_data.min(), self.p_data.max()])
        else:
            return False
        self._needUpdate = True
        return True

    def setVectorData(self, data, forceUpd=True, minmaxUpd=True):
        if forceUpd:
            self._needUpdate = True
        if self.p_data is data:
            return True
        if isinstance(data, np.ndarray) and len(data.shape) == 4:
            if data.shape[3] > 3:
                self.p_data \
                    = data[:, :, :, :, 0:3].astype(np.float32, copy=False)
            elif data.shape[3] == 3:
                self.p_data = data.astype(np.float32, copy=False)
            else:
                return False
            if minmaxUpd:
                maxVecLen = np.sqrt((self.p_data**2).sum(axis=-1)).max()
                self.setMinMax([0.0, maxVecLen])
        else:
            return False
        self._needUpdate = True
        return True

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
                if coord.dtype == np.float32:
                    self.p_coord = coord[:dims[0], :dims[1], :dims[2], :]
                else:
                    self.p_coord = np.empty((dims[0], dims[1], dims[2], 3),
                                            dtype=np.float32)
                    self.p_coord[:,:,:,:] = coord[:dims[0],:dims[1],:dims[2],:]
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
            self.p_coord = np.stack([Xg, Yg, Zg], axis=-1, dtype=np.float32)
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
            self.p_coord = np.stack([Xg, Yg, Zg], axis=-1, dtype=np.float32)
            self._needUpdate = True
        except:
            return False
        return True

#----------------------------------------------------------------------
class VisRegOrthoSlice(VisRegularMesh):
    """ VisRegOrthoSliceクラス
        Base class of orthogonal slicer implemented for regular mesh
    """

    # slice axes
    (S_Za, S_Ya, S_Xa) = range(3)

    def __init__(self, **args):
        VisRegularMesh.__init__(self, **args)

        self._slicePlane = self.S_Za
        self._sliceIndex = -1

        return

    def getVisObjType(self):
        return "OrthoSlice"

    def setSliceParam(self, slicePlane=-1, sliceIndex=-1, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if slicePlane in (self.S_Za, self.S_Xa, self.S_Ya):
            if slicePlane != self._slicePlane:
                self._slicePlane = slicePlane
                self._needUpdate = True
        if sliceIndex >= 0 and self._sliceIndex != sliceIndex:
            self._sliceIndex = sliceIndex
            self._needUpdate = True
        return True

    def parseParamArgs(self, **args):
        slicePlane = -1 if not 'slicePlane' in args else args['slicePlane']
        sliceIndex = -1 if not 'sliceIndex' in args else args['sliceIndex']
        return (slicePlane, sliceIndex)

    def orthoSlice(self, p_data):
        cslice, dslice = (None, None)
        
        if self.p_coord is None:
            return (cslice, dslice)

        dims = self.p_coord.shape
        if self._slicePlane == self.S_Za:
            S = dims[0]
        elif self._slicePlane == self.S_Xa:
            S = dims[2]
        else: # S_Ya
            S = dims[1]
        if self._sliceIndex < 0:
            self._sliceIndex = int(S / 2)
        elif self._sliceIndex >= S:
            self._sliceIndex = S -1

        if self._slicePlane == self.S_Za:
            cslice = np.ascontiguousarray(self.p_coord[self._sliceIndex,:,:,:])
            if not p_data is None:
                dslice = np.ascontiguousarray(p_data[self._sliceIndex,:,:])
        elif self._slicePlane == self.S_Xa:
            cslice = np.ascontiguousarray(self.p_coord[:,:,self._sliceIndex,:])
            if not p_data is None:
                dslice = np.ascontiguousarray(p_data[:,:,self._sliceIndex])
        else: # S_Ya
            cslice = np.ascontiguousarray(self.p_coord[:,self._sliceIndex,:,:])
            if not p_data is None:
                dslice = np.ascontiguousarray(p_data[:,self._sliceIndex,:])

        return (cslice, dslice)

    def insertSlicePP(self, sizerTop):
        if self.paramsPnl is None or sizerTop is None:
            return False

        self._slicePlaneButtons = []

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

        return True

    def updateSlicePP(self):
        if self.paramsPnl is None or \
           len(self._slicePlaneButtons) < 1 or \
           self._sliceIndexSld is None or self._sliceIndexTxt is None:
            return False

        # slicePlane
        if self._slicePlane == self.S_Ya:
            self._slicePlaneButtons[self.S_Ya].SetValue(True)
        elif self._slicePlane == self.S_Xa:
            self._slicePlaneButtons[self.S_Xa].SetValue(True)
        else:
            self._slicePlaneButtons[self.S_Za].SetValue(True)

        # sliceIndex
        if not self.p_data is None and len(self.p_data.shape) in (3, 4):
            self._sliceIndexSld.SetRange(0, self.p_data.shape[self._slicePlane])
            if self._sliceIndex < 0:
                self._sliceIndex = int(self.p_data.shape[self._slicePlane]/2)
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))

        return True

    # Event Handlers

    def OnSlicePlaneRadio(self, event):
        if self.p_data is None or not len(self.p_data.shape) in (3, 4):
            return
        new_sliceAxs = None
        if self._slicePlaneButtons[self.S_Za].GetValue() == True:
            new_sliceAxs = self.S_Za
        elif self._slicePlaneButtons[self.S_Ya].GetValue() == True:
            new_sliceAxs = self.S_Ya
        elif self._slicePlaneButtons[self.S_Xa].GetValue() == True:
            new_sliceAxs = self.S_Xa
        if new_sliceAxs is None:
            new_sliceAxs = self.S_Za
            self._slicePlaneButtons[self.S_Za].SetValue(True)
        if self._slicePlane == new_sliceAxs:
            return

        if self.setSliceParam(slicePlane=new_sliceAxs):
            self._sliceIndexSld.SetRange(0, self.p_data.shape[self._slicePlane])
            if self.update():
                self.chkNotice()
        return

    def OnSliceIndexSld(self, event):
        if self.p_data is None or not len(self.p_data.shape) in (3, 4):
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
        if self.p_data is None or not len(self.p_data.shape) in (3, 4):
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
        if self.p_data is None or not len(self.p_data.shape) in (3, 4):
            return
        if self.setSliceParam(sliceIndex=self._sliceIndex -1):
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            if self.update():
                self.chkNotice()
        return

    def OnSlicePlusBtn(self, event):
        if self.p_data is None or not len(self.p_data.shape) in (3, 4):
            return
        if self.setSliceParam(sliceIndex=self._sliceIndex +1):
            self._sliceIndexSld.SetValue(self._sliceIndex)
            self._sliceIndexTxt.SetValue(str(self._sliceIndex))
            if self.update():
                self.chkNotice()
        return
