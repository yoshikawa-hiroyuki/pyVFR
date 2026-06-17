#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegOrthoSlice
"""
import sys, os
import numpy as np
import ctypes as C
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisRegularMesh import *


#----------------------------------------------------------------------
vsn_impl = np.ctypeslib.load_library('vsn_impl',
                                     os.path.join(os.path.dirname(__file__),
                                                  "lib"))
vsn_impl.GenerateIsosurfS.restype = C.c_int
vsn_impl.GenerateIsosurfS.argtypes = [
    C.c_void_p,             # p
    C.c_size_t*3,           # dims[3]
    C.POINTER(C.c_float*3), # coord
    C.POINTER(C.c_float),   # data
    C.c_float               # thresh
]

vsn_impl.GenerateIsosurfD.restype = C.c_int
vsn_impl.GenerateIsosurfD.argtypes = [
    C.c_void_p,             # p
    C.c_size_t*3,           # dims[3]
    C.POINTER(C.c_float*3), # coord
    C.POINTER(C.c_double),  # data
    C.c_double              # thresh
]

vector3 = C.c_float * 3

#----------------------------------------------------------------------
class VisRegIsosurf(VisRegularMesh):
    """ VisRegIsosurfクラス
        show isosurface of regular mesh
    """

    def __init__(self, **args):
        """
        args: data =None, bbox =None, orgPitch =None, coord =None,
              isoValue =None, useLut =True, useLutAlpha =False, minMax =None
        """
        VisRegularMesh.__init__(self, **args)

        self.p_data = None
        self._isoValue = None
        self._useLut = True
        self._useLutAlpha = False

        self._surf = triangles.Triangles(name='Isosurf_Tria',
                                         localMaterial=False)
        self._surf.setNormalMode(gfxNode.AT_PER_VERTEX)
        self.addChild(self._surf)

        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "Isosurf"

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
    
    def setIsoValue(self, isoValue, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if isoValue != None and isoValue != self._isoValue:
            self._isoValue = isoValue
            self._needUpdate = True
        return True

    def setUseLut(self, useLut=None, useLutAlpha=None, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        if not useLut is None and useLut != self._useLut:
            self._useLut = useLut
            self._needUpdate = True
        if not useLutAlpha is None and useLutAlpha != self._useLutAlpha:
            self._useLutAlpha = useLutAlpha
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

    def setBaseOpac(self, opac):
        """ setBaseOpac -- override VisObj.setBaseOpac
        """
        if self._useLutAlpha == False:
            VisObj.setBaseOpac(self, opac)
            return
        self._colors[0][3] = opac
        self.notice()
        return

    def update(self, **args):
        # check initialized
        if not self._surf:
            return False

        # pickup args
        data = None if not 'data' in args else args['data']
        minmax = None if not 'minMax' in args else args['minMax']
        (coord, bbox, o_p) = VisRegularMesh.getCoordArgs(self, **args)
        lut = None if not 'lut' in args else args['lut']

        isoValue = None if not 'isoValue' in args else args['isoValue']
        useLut = True if not 'useLut' in args else args['useLut']
        useLutAlpha = False if not 'useLutAlpha' in args \
            else args['useLutAlpha']

        if not data is None:
            self.setData(data, False)
        if not minmax is None:
            self.setMinMax(minmax, False)
        elif not self.p_data is None:
            self.setMinMax([self.p_data.min(), self.p_data.max()], False)
        if not coord is None:
            self.setCoord(coord, False)
        elif not bbox is None:
            self.setCoordByBbox(bbox, False)
        elif not o_p is None:
            self.setCoordByOrgPitch(o_p, False)
        if not lut is None:
            self.lut.setTo(lut)
            self._needUpdate = True

        if isoValue is None:
            if not self.p_data is None:
                isoValue = (self.p_data.min() + self.p_data.max()) * 0.5
                self.setIsoValue(isoValue, False)
        else:
            self.setIsoValue(isoValue, False)
            
        self.setUseLut(useLut, useLutAlpha, False)

        if not self._needUpdate:
            return True

        # update self._surf from 
        if self.p_data is None or self.p_coord is None:
            return False

        dims = (C.c_size_t*3)(self.p_data.shape[2], self.p_data.shape[1],
                              self.p_data.shape[0])
        coord_ptr = self.p_coord.ctypes.data_as(C.POINTER(vector3))
        if self.p_data.dtype == np.float32:
            data_ptr = self.p_data.ctypes.data_as(C.POINTER(C.c_float))
            ret = vsn_impl.GenerateIsosurfS(self._surf.p_impl,
                                            dims, coord_ptr, data_ptr,
                                            C.c_float(self._isoValue))
            if ret:
                self._surf.updateObjImpl()
                self._surf.generateBbox()
                self._surf.generateNormals()
        elif self.p_data.dtype == np.float64:
            data_ptr = self.p_data.ctypes.data_as(C.POINTER(C.c_double))
            ret = vsn_impl.GenerateIsosurfD(self._surf.p_impl,
                                            dims, coord_ptr, data_ptr,
                                            C.c_double(self._isoValue))
            if ret:
                self._surf.updateObjImpl()
                self._surf.generateBbox()
                self._surf.generateNormals()
        
        # update show mode
        if self._useLut and self._isoValue != None:
            cidx = self.lut.getValIdx(self._isoValue)
            self._surf._colors[0][0:3] = self.lut.entry[cidx, 0:3]
        else:
            self._surf._colors[0][0:3] = self._colors[0][0:3]
        if self._useLutAlpha and self._isoValue != None:
            cidx = self.lut.getValIdx(self._isoValue)
            self._surf._colors[0][3] = self.lut.entry[cidx, 3]
        else:
            self._surf._colors[0][3] = self._colors[0][3]
        self._surf.setTransparency(self._surf._colors[0][3] < 0.98)

        self.generateBbox()
        self._needUpdate = False
        return True

    def initPP(self):
        if self.paramsPnl is None:
            return False

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # isoValue
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='isoValue'))
        self._isoValueTxt = wx.TextCtrl(self.paramsPnl, value='0.0', \
                                        style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._isoValueTxt, flag=wx.EXPAND|wx.ALL, \
                   proportion=1, border=3)
        self._isoValueTxt.Bind(wx.EVT_TEXT_ENTER, self.OnIsoValueTxt)

        # useLut, useLutAlpha
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._useLutChk = wx.CheckBox(self.paramsPnl, label='use Lut color')
        sizerH.Add(self._useLutChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._useLutChk.Bind(wx.EVT_CHECKBOX, self.OnUseLutChk)

        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self._useLutAlphaChk = wx.CheckBox(self.paramsPnl,
                                           label='use Lut alpha')
        sizerH.Add(self._useLutAlphaChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._useLutAlphaChk.Bind(wx.EVT_CHECKBOX, self.OnUseLutAlphaChk)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True

    def updatePP(self):
        if self.paramsPnl is None:
            return False

        # isoValue
        self._isoValueTxt.SetValue(str(self._isoValue))

        # useLut, useLutAlpha
        self._useLutChk.SetValue(self._useLut)
        self._useLutAlphaChk.SetValue(self._useLutAlpha)

        return True

    # Event Handlers

    def OnIsoValueTxt(self, event):
        try:
            val = float(self._isoValueTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return

        if val == self._isoValue:
            return
        if self.update(isoValue=val):
            self.chkNotice()
        return

    def OnUseLutChk(self, event):
        val = self._useLutChk.GetValue()
        if val == self._useLut:
            return
        if self.update(useLut=val):
            self.chkNotice()
        return

    def OnUseLutAlphaChk(self, event):
        val = self._useLutAlphaChk.GetValue()
        if val == self._useLutAlpha:
            return
        if self.update(useLutAlpha=val):
            self.chkNotice()
        return


if __name__ == '__main__':
    from pySPH import SPH
    import App
    app = App.GetVsnApp()
    arena = app.getArena()

    files = [f"p_{i:03d}.sph" for i in range(1, 11)]
    sph = SPH.SPH()
    sph.load(os.path.join("data", files[-1]))

    isosurf = VisRegIsosurf(name='TestIsosurf', data=sph.dataIndexed(),
                            orgPitch=[sph.org, sph.pitch])
    arena.addObject(isosurf)
    app.run(debug=True)

