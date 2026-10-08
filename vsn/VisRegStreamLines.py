#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoVector
"""
import sys, os
import numpy as np
import ctypes as C
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisRegularMesh import *
from VisSampler import *
from LineStripSet import *

#----------------------------------------------------------------------
vsn_impl = np.ctypeslib.load_library('vsn_impl',
                                     os.path.join(os.path.dirname(__file__),
                                                  "lib"))
vsn_impl.CreateStreamLineObj.restype = C.c_void_p
vsn_impl.CreateStreamLineObj.argtypes = [
    C.c_int,    # divTime
    C.c_int,    # numSkip
    C.c_int,    # maxPts
]

vsn_impl.DeleteStreamLineObj.restype = C.c_int
vsn_impl.DeleteStreamLineObj.argtypes = [
    C.c_void_p, # p
]

vsn_impl.CalcStreamLines.restype = C.c_int
vsn_impl.CalcStreamLines.argtypes = [
    C.c_void_p,             # p
    C.c_void_p,             # q
    C.c_size_t,             # ns
    C.POINTER(C.c_float*3), # samplePts
    C.c_size_t*3,           # dims[3]
    C.POINTER(C.c_float*3), # coord
    C.POINTER(C.c_float),   # data
]

#----------------------------------------------------------------------
class VisRegStreamLines(VisRegularMesh, SampleReceiver):
    """ VisRegStreamLinesクラス
        show streamlines of regular mesh vector data
    """

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              samplePts =None, useLut =False, coloredLine =False,
              lineWidth =1.0, divTime =4, skipStep =1, maxPoints =1000
        """
        VisRegularMesh.__init__(self, **args)
        self.showType = gfxNode.RT_WIRE

        self.p_slimpl = None
        self.p_data = None
        self._useLut = False
        self._coloredLine = False
        self._divTime = 4
        self._skipStep = 1
        self._maxPoints = 1000
        self._sampleDims = [0, 0, 0]
        self._samplePts = None

        self._lines = vsnLineStripSet(name='StreamLines_LineStripSet',
                                      localMaterial=False)
        self.addChild(self._lines)

        if self.update(**args):
            self.show = True
        return

    def destroy(self):
        if not self.p_slimpl is None:
            vsn_impl.DeleteStreamLineObj(self.p_slimpl)
            self.p_slimpl = None
        VisObj.destroy(self)
        
    def getVisObjType(self):
        return "StreamLines"

    def setData(self, data, forceUpd=True, minmaxUpd=True):
        return VisRegularMesh.setVectorData(self, data, forceUpd, minmaxUpd)

    def setSamplePts(self, samplePts, forceUpd=True):
        self._sampleDims = [0, 0, 0]
        if forceUpd:
            self._needUpdate = True
        if isinstance(samplePts, np.ndarray) and \
           len(samplePts.shape) in (2, 3, 4) and samplePts.shape[-1] == 3:
            sampleDims = [1, 1, 1]
            if samplePts.shape == 2:
                sampleDims[0] = samplePts.shape[0]
                nv = sampleDims[0]
                if nv < 1:
                    return False
                self._samplePts = samplePts.astype(np.float32)
            elif samplePts.shape == 3:
                sampleDims[0] = samplePts.shape[0]
                sampleDims[1] = samplePts.shape[1]
                nv = sampleDims[0] * sampleDims[1]
                if nv < 1:
                    return False
                self._samplePts = samplePts.astype(np.float32).reshape(nv, 3)
            else: # samplePts.shape == 4
                sampleDims[0] = samplePts.shape[0]
                sampleDims[1] = samplePts.shape[1]
                sampleDims[2] = samplePts.shape[2]
                nv = sampleDims[0] * sampleDims[1] * sampleDims[2]
                if nv < 1:
                    return False
                self._samplePts = samplePts.astype(np.float32).reshape(nv, 3)
            self._sampleDims[:] = sampleDims[:]
            self._needUpdate = True
        return True

    def setBaseColor(self, color):
        """ setBaseColor -- override VisObj.setBaseColor
        """
        if self._useLut == False and self._coloredLine == False:
            VisObj.setBaseColor(self, color)
            return
        self._colors[0][0:3] = color[0:3]
        self.notice()
        return

    def receive(self, sampler):
        vts = sampler.getSamplePointCoord()
        self.update(samplePts=vts)
        return

    def setIntegralParam(self, divTime =-1, skipStep =-1, maxPoints =-1,
                         forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if divTime > 0 and divTime != self._divTime:
            self._divTime = divTime
            self._needUpdate = True
        if skipStep > 0 and skipStep != self._skipStep:
            self._skipStep = skipStep
            self._needUpdate = True
        if maxPoints > 0 and maxPoints != self._maxPoints:
            self._maxPoints = maxPoints
            self._needUpdate = True
        if self._needUpdate:
            if not self.p_slimpl is None:
                vsn_impl.DeleteStreamLineObj(self.p_slimpl)
            self.p_slimpl = vsn_impl.CreateStreamLineObj(self._divTime,
                                                         self._skipStep,
                                                         self._maxPoints)
            if self.p_slimpl is None:
                return False
        return True

    def update(self, **args):
        # check initialized
        if self._lines is None:
            return False

        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        (coord, bbox, o_p) = VisRegularMesh.getCoordArgs(self, **args)
        lut = None if not 'lut' in args else args['lut']

        samplePts = None if not 'samplePts' in args else args['samplePts']

        divTime = -1 if not 'divTime' in args else args['divTime']
        skipStep = -1 if not 'skipStep' in args else args['skipStep']
        maxPoints = -1 if not 'maxPoints' in args else args['maxPoints']
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

        self.setSamplePts(samplePts, False)
        self.setIntegralParam(divTime, skipStep, maxPoints, False)
        if lineWidth > 0.0:
            self.setLineWidth(lineWidth)

        if not self._needUpdate:
            return True

        # update mesh coord and data
        p_data = None if self.p_data is None else self.p_data
        if self.p_coord is None or p_data is None:
            return False
        max_veclen = np.linalg.norm(self.p_coord, axis=-1).max()

        # check samplePts(_verts)
        nv = self._sampleDims[0]*self._sampleDims[1]*self._sampleDims[2]
        if nv < 1:
            return False

        # calculate streamlines
        if self.p_slimpl is None:
            return False
        sample_ptr = self._samplePts.ctypes.data_as(C.POINTER(C.c_float*3))
        dims = (C.c_size_t*3)(self.p_data.shape[2], self.p_data.shape[1],
                              self.p_data.shape[0])
        coord_ptr = self.p_coord.ctypes.data_as(C.POINTER(C.c_float*3))
        data_ptr = self.p_data.ctypes.data_as(C.POINTER(C.c_float))
        ret = vsn_impl.CalcStreamLines(self.p_slimpl, self._lines.p_impl,
                                       nv, sample_ptr,
                                       dims, coord_ptr, data_ptr)
        if not ret:
            return False
        self._lines.updateObjImpl()
        self._lines.generateBbox()
        self._lines.notice()

        # setup lines color

        self.generateBbox()
        self._needUpdate = False
        return True

    def initPP(self):
        if self.paramsPnl is None:
            return False

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # line width
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='line width'), border=3)
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
        if self.paramsPnl is None:
            return False

        # line width
        self._lineWidthTxt.SetValue(str(self.getLineWidth()))

        return True

    # Event Handlers

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
    sph.load(os.path.join("data", "uvw_010.sph"))
    gro = [sph.org[0] + sph.pitch[0]*(sph.dims[0]-1),
           sph.org[1] + sph.pitch[1]*(sph.dims[1]-1),
           sph.org[2] + sph.pitch[2]*(sph.dims[2]-1)]

    streamliner = VisRegStreamLines(name='TestStreamLine',
                                    data=sph.dataIndexed(),
    #                               orgPitch=[sph.org, sph.pitch])
                                    bbox=[sph.org, gro])
    arena.addObject(streamliner)

    sampler = VisSampler(name='TestSampler')
    arena.addObject(sampler)
    sampler.addReceiver(streamliner)

    bounds = VisRegBounds(name='TestBounds', data=sph.dataIndexed(),
                          orgPitch=[sph.org, sph.pitch])
    arena.addObject(bounds)

    app.run(debug=True)
