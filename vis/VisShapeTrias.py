#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisSampler
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *

#----------------------------------------------------------------------

class VisShapeTrias(VisObj):
    """ VisShapeTriasrクラス
    """

    def __init__(self, **args):
        """
        args: showMode =gfxNode.RT_SHADING, lineWidth =1.0, ptSize =3.0,
              filePath =None, fileFmt =None, coords =None, norms =None,
              indices =None
        """
        VisObj.__init__(self, **args)
        self.showType = gfxNode.RT_SHADING

        if self.update(**args):
            self.show = True
        return

    def getVisObjType(self):
        return "Trias"

    def loadFile(self, filePath, fileFmt =None):
        self.remAllChildren()

        (trias, _) = tria_io.Read(filePath, fileFmt)
        if trias is None:
            raise Exception(f"file load failed: path={filePath}, fmt={fileFmt}")
        if not self.addChild(trias):
            return False

        self._needUpdate = True
        return True

    def setCoords(self, coords, norms =None, indices =None, forceUpd=True):
        if forceUpd:
            self._needUpdate = True
        self.remAllChildren()

        p_coords = coords.reshape(-1, 3).astype(np.float32)

        trias = triangles.Triangles(name='Trias_trias', localMaterial=False)
        if trias is None:
            return False
        trias.setNormalMode(gfxNode.AT_PER_VERTEX)
        self.addChild(trias)

        p_norms = None        
        if not norms is None:
            p_norms = norms.reshape(-1, 3).astype(np.float32)
        
        if not indices is None:
            # treat as indexed triangle set
            trias.alcData(nV=len(indices), nN=len(indices))
            vl = trias._verts
            idx = 0
            for i in indices:
                vl[idx][:] = p_coords[i][:]
                idx += 1
                continue # end of for(i)
            if not p_norms is None:
                nl = trias._normals
                idx = 0
                for i in indices:
                    nl[idx][:] = p_norms[i][:]
                    idx += 1
                    continue # end of for(i)
        else:
            # treat as triangle stack
            nv = p_coords.shape[0]
            trias.alcData(nV=nv, nN=nv)
            vl = trias._verts
            for i in range(nv):
                vl[i][:] = p_coords[i][:]
                continue # end of for(i)
            if not p_norms is None:
                nl = trias._normals
                for i in range(nv):
                    nl[i][:] = p_norms[i][:]
                    continue # end of for(i)

        if norms is None:
            trias.generateNormals()

        self._needUpdate = True
        return True

    def update(self, **args):
        # pickup args
        showMode = None if not 'showMode' in args else args['showMode']
        lineWidth = -1.0 if not 'lineWidth' in args else args['lineWidth']
        ptSize = -1.0 if not 'ptSize' in args else args['ptSize']
        filePath = None if not 'filePath' in args else args['filePath']
        fileFmt = None if not 'fileFmt' in args else args['fileFmt']
        coords = None if not 'coords' in args else args['coords']
        norms = None if not 'norms' in args else args['norms']
        indices = None if not 'indices' in args else args['indices']

        if not showMode is None:
            self.setRenderMode(showMode)
            self.showType = showMode
            self._needUpdate = True
        if not lineWidth < 0.0:
            self.setLineWidth(lineWidth)
            self._needUpdate = True
        if not ptSize < 0.0:
            self.setPointSize(ptSize)
            self._needUpdate = True
        if not filePath is None:
            if self.loadFile(filePath, fileFmt):
                self._needUpdate = True
        if not coords is None:
            self.setCoords(coords, norms, indices, False)

        if not self._needUpdate:
            return True
        
        self.generateBbox()
        self._needUpdate = False
        return True

    def initPP(self):
        if self.paramsPnl is None:
            return False

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # showMode
        self._showModeButtons = []
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='show mode'))
        choices = ["Faces", "Lines", "Points"]
        for i, choice in enumerate(choices):
            style = wx.RB_GROUP if i == 0 else 0
            rb = wx.RadioButton(self.paramsPnl, label=choice, style=style)
            rb.Bind(wx.EVT_RADIOBUTTON, self.OnShowModeRadio)
            sizerH.Add(rb, flag=wx.ALL, border=3)
            self._showModeButtons.append(rb)
            continue # for i,choice

        # line_width
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='line width'), border=3)
        self._lineWidthTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._lineWidthTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._lineWidthTxt.Bind(wx.EVT_TEXT_ENTER, self.OnLineWidthTxt)

        # point_size
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='point size'), border=3)
        self._pointSizeTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._pointSizeTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._pointSizeTxt.Bind(wx.EVT_TEXT_ENTER, self.OnPointSizeTxt)

        # filePath, fileFmt ... no UI
        # coords, norms, indices ... no UI

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True

    def updatePP(self):
        if self.paramsPnl is None:
            return False

        # showMode
        if self.showType == gfxNode.RT_SHADING:
            self._showModeButtons[0].SetValue(True)
        elif self.showType == gfxNode.RT_WIRE:
            self._showModeButtons[1].SetValue(True)
        elif self.showType == gfxNode.RT_POINT:
            self._showModeButtons[2].SetValue(True)

        # line_width
        self._lineWidthTxt.SetValue(str(self.getLineWidth()))

        # point_size
        self._pointSizeTxt.SetValue(str(self.getPointSize()))

        return True

    # Event Handlers

    def OnShowModeRadio(self, event):
        new_showType = None
        if self._showModeButtons[0].GetValue() == True:
            new_showType = gfxNode.RT_SHADING
        elif self._showModeButtons[1].GetValue() == True:
            new_showType = gfxNode.RT_WIRE
        elif self._showModeButtons[2].GetValue() == True:
            new_showType = gfxNode.RT_POINT

        if new_showType is None:
            new_showType = gfxNode.RT_SHADING
            self._showModeButtons[0].SetValue(True)
        if self.showType == new_showType:
            return

        if self.update(showMode=new_showType):
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
            for c in self._children:
                c.setLineWidth(val)
                c.notice()
            self.chkNotice()
        return

    def OnPointSizeTxt(self, event):
        try:
            val = float(self._pointSizeTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val <= 0.0:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val != self._pointSize:
            self.setPointSize(val)
            for c in self._children:
                c.setPointSize(val)
                c.notice()
            self.chkNotice()
        return


if __name__ == '__main__':
    import App
    app = App.GetVsnApp()
    arena = app.getArena()

    trias = VisShapeTrias(name='TestTrias')
    trias.loadFile('data/cube.obj')
    trias.setS((1.0, 2.0, 3.0))
    arena.addObject(trias)

    app.run(debug=True)
    
