#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisSampler
"""
import sys, os
import numpy as np
import ctypes as C
import copy
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *

#----------------------------------------------------------------------
class SampleReceiver(node.Node):
    def __init__(self, **args):
        node.Node.__init__(self, **args)
        return

    def receive(self, sampler):
        pass

#----------------------------------------------------------------------
class VisSampler(VisObj):
    """ VisSamplerクラス
        Base class of Sampler VisObj
    """

    def __init__(self, **args):
        """
        args: nx =3, ny =3, nz =1, showPt =True, ptSize =3.0
        """
        VisObj.__init__(self, **args)
        self.showType = gfxNode.RT_POINT
        
        self._gridDims = [3, 3, 1]
        self._showPt = True
        self.setPointSize(3.0)

        self._ptSet = primSet.PrimSet(name='Sampler_PtSet', localMaterial=False)
        self.addChild(self._ptSet)

        self._receiverGrp = gfxGroup.GfxGroup(name='Sampler_Receiver')

        if self.update(**args):
            self.show = True
        return

    def destroy(self):
        del self._receiverGrp
        VisObj.destroy(self)

    def getVisObjType(self):
        return "Sampler"

    def addReceiver(self, receiver):
        if not isinstance(receiver, SampleReceiver):
            return False
        return self._receiverGrp.addChild(receiver)

    def remReceiver(self, receiver):
        return self._receiverGrp.remChild(receiver)

    def setGridDims(self, nx=-1, ny=-1, nz=-1, forceUpd=True):
        if forceUpd:
            self._needUpdate = True

        gdims = copy.copy(self._gridDims)
        if nx > 0: gdims[0] = nx
        if ny > 0: gdims[1] = ny
        if nz > 0: gdims[2] = nz
        if gdims != self._gridDims:
            self._gridDims = gdims
            self._needUpdate = True
        return True

    def setShowPt(self, showPt=True, ptSize=-1.0, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if showPt != self._showPt:
            self._showPt = showPt
            self._needUpdate = True
        if ptSize > 0.0 and ptSize != self._pointSize:
            self.setointSize(ptSize)
            if self._showPt:
                self._needUpdate = True
        return True

    def update(self, **args):
        # check initialized
        if not self._ptSet:
            return False

        # pickup args
        nx = -1 if not 'nx' in args else args['nx']
        ny = -1 if not 'ny' in args else args['ny']
        nz = -1 if not 'nz' in args else args['nz']
        showPt = True if not 'showPt' in args else args['showPt']
        ptSize = -1.0 if not 'ptSize' in args else args['ptSize']

        self.setGridDims(nx, ny, nz, False)
        self.setShowPt(showPt, ptSize, False)

        if not self._needUpdate:
            return True

        # generate points coord
        nx, ny, nz = tuple(self._gridDims)
        nc = nx * ny * nz
        dx = 1.0/(nx - 1) if nx > 1 else 1.0
        dy = 1.0/(ny - 1) if ny > 1 else 1.0
        dz = 1.0/(nz - 1) if nz > 1 else 1.0
        pos = [0.0, 0.0, 0.0]
        if nc < 1 or not self._ptSet.alcData(nV=nc):
            return False
        for k in range(nz):
            pos[1] = 0.0
            for j in range(ny):
                pos[0] = 0.0
                for i in range(nx):
                    self._ptSet._verts[nx*ny*k +nx*j +i][:] = pos[:]
                    pos[0] += dx
                    continue # i
                pos[1] += dy
                continue # j
            pos[2] += dz
            continue # k
        self._ptSet.generateBbox()
        self._ptSet.notice()

        # call receive of all receiver
        for refer in self._receiverGrp._children:
            refer.receive(self)

        # update show mode
        showType = gfxNode.RT_NONE
        if self._showPt:
            showType = gfxNode.RT_POINT
        self._ptSet.setRenderMode(showType)

        self.generateBbox()
        self._needUpdate = False
        return True

    def getSamplePointCoord(self, in3d=False):
        if not self.update():
            return None
        nV = self._ptSet.getNumVerts()
        if nV < 1:
            return None

        vts = np.np.ndarray((nV,3))
        M = self.getXFormMatrix()
        for i in range(nV):
            v = self._ptSet._verts[i]
            vv = M * v
            vts[i][:] = vv[:]
            continue # i

        if not in3d:
            return vts
        nx, ny, nz = tuple(self._gridDims)
        return vts.reshape((nz, ny, nx, 3))
    
    def initPP(self):
        if self.paramsPnl is None:
            return False

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # gridDims
        nx, ny, nz = tuple(self._gridDims)
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='sample pt num'))
        self._nxTxt = wx.TextCtrl(self.paramsPnl, value=str(int(nx)), \
                                  size=wx.Size(50,-1),
                                  style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._nxTxt, flag=wx.EXPAND|wx.ALL, border=3)
        self._nxTxt.Bind(wx.EVT_TEXT_ENTER, self.OnGridDimsTxt)
        self._nyTxt = wx.TextCtrl(self.paramsPnl, value=str(int(ny)), \
                                  size=wx.Size(50,-1),
                                  style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._nyTxt, flag=wx.EXPAND|wx.ALL, border=3)
        self._nyTxt.Bind(wx.EVT_TEXT_ENTER, self.OnGridDimsTxt)
        self._nzTxt = wx.TextCtrl(self.paramsPnl, value=str(int(nz)), \
                                  size=wx.Size(50,-1),
                                  style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._nzTxt, flag=wx.EXPAND|wx.ALL, border=3)
        self._nzTxt.Bind(wx.EVT_TEXT_ENTER, self.OnGridDimsTxt)

        # showPt
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._showPtChk = wx.CheckBox(self.paramsPnl, label='show point')
        sizerH.Add(self._showPtChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._showPtChk.Bind(wx.EVT_CHECKBOX, self.OnShowPtChk)
        
        # pointSize
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='point size'))
        self._pointSizeTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._pointSizeTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._pointSizeTxt.Bind(wx.EVT_TEXT_ENTER, self.OnPointSizeTxt)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True

    def updatePP(self):
        if self.paramsPnl is None or \
           self._nxTxt is None or self._nyTxt is None or self._nzTxt is None \
           or self._showPtChk is None or self._pointSizeTxt is None:
            return False

        # gridDims
        nx, ny, nz = tuple(self._gridDims)
        self._nxTxt.SetValue(str(int(nx)))
        self._nyTxt.SetValue(str(int(ny)))
        self._nzTxt.SetValue(str(int(nz)))

        # showPt
        self._showPtChk.SetValue(self._showPt)

        # pointSize
        self._pointSizeTxt.SetValue(str(self.getPointSize()))

        return True

    # Event Handlers

    def OnGridDimsTxt(self, event):
        try:
            nx = int(self._nxTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            nx = self._gridDims[0]
            self._nxTxt.SetValue(str(int(nx)))
        try:
            ny = int(self._nyTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            ny = self._gridDims[1]
            self._nyTxt.SetValue(str(int(ny)))
        try:
            nz = int(self._nzTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            nz = self._gridDims[2]
            self._nzTxt.SetValue(str(int(nz)))

        if self.update(nx=nx, ny=ny, nz=nz):
            self.chkNotice()
        return

    def OnShowPtChk(self, event):
        val = self._showPtChk.GetValue()
        if self.update(showPt=val):
            self.chkNotice()
        return

    def OnPointSizeTxt(self, event):
        try:
            val = float(self._pointSizeTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self._pointSizeTxt.SetValue(str(self.getPointSize()))
            return
        if val <= 0.0:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self._pointSizeTxt.SetValue(str(self.getPointSize()))
            return
        if val != self.getPointSize():
            self.setPointSize(val)
            self.chkNotice()
        return


if __name__ == '__main__':
    import App
    app = App.GetVsnApp()
    arena = app.getArena()

    sampler = VisSampler(name='TestSampler')
    arena.addObject(sampler)

    app.run(debug=True)

    
