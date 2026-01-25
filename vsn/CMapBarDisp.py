#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""CMapBarDisp implementation
  CMapBarDispクラス, Front表示のCMapBarクラスを提供します.
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *
import FrontObj


#----------------------------------------------------------------------
# CMapBarDisp class implementation

class CMapBarDisp(FrontObj.FrontObj):
    """ CMapBarDispクラス
    """
    (CBD_VERTICAL, CBD_HORIZONTAL) = range(2)
    CBD_TITLE_SIZE = 0.08
    CBD_LABEL_SIZE = 0.05

    
    def __init__(self, **args):
        """ 初期設定.
        """
        FrontObj.FrontObj.__init__(self, **args)
        self.setPickMode(gfxNode.PT_OBJECT)
        self.setRenderMode(gfxNode.RT_NOLIGHT)
        
        self.lut = lut.Lut()
        self.ref = None if not 'ref' in args else args['ref']
        if self.ref:
            self.lut.setTo(self.ref.lut)

        self.numLbls = 2
        self.precLbls = 2
        self.direction = CMapBarDisp.CBD_VERTICAL
        self.showAlpha = False

        self.pBar = mesh.Mesh2D(name='CMapBarDisp_Bar', localMaterial=False)
        self.pBar.setColorMode(gfxNode.AT_PER_FACE)
        self.pBar.setBboxShowMode(True)
        self.pBar.setBboxWidth(1.0)
        self.addChild(self.pBar)

        self.pTitleLbl = letters.Letters(name='CMapBarDisp_Title',
                                         localMaterial=False,
                                         font=letters.FONT_LINE,
                                         fontScale=CMapBarDisp.CBD_TITLE_SIZE)
        self.pTitleLbl.setTransparency(True)
        self.addChild(self.pTitleLbl)

        self.pLbls = gfxGroup.GfxGroup(name='CMapBarDisp_Lbls',
                                       localMaterial=False)
        self.addChild(self.pLbls)

        self.sz = [0.2, 1.0]
        self.setPosition(0.7, 0.0)

        self.update()
        return

    
    def update(self):
        # reset
        self.pBar.identity()
        self.pTitleLbl.identity()
        self.pLbls.identity()
        if not self.ref: return

        # bar
        v = [0.0, 0.0, 0.0]
        self.pBar.setMeshSize(self.lut.numEntry +1, 3)
        self.pBar.alcData(nC=self.lut.numEntry*2)
        if self.direction == CMapBarDisp.CBD_HORIZONTAL:
            dv = self.sz[0] / self.lut.numEntry
            for i in range(self.lut.numEntry+1):
                v[0] = i * dv
                v[1] = 0.2 * self.sz[1]
                self.pBar.setVert(i, v, False)
                v[1] = 0.55 * self.sz[1]
                self.pBar.setVert(i +self.lut.numEntry +1, v, False)
                v[1] = 0.7 * self.sz[1]
                self.pBar.setVert(i +(self.lut.numEntry+1)*2, v, False)
                continue # end of for i
        else:
            dv = 0.7 * self.sz[1] / self.lut.numEntry
            for i in range(self.lut.numEntry+1):
                v[0] = 0.45 * self.sz[0]
                v[1] = i * dv
                self.pBar.setVert(i, v, False)
                v[0] = 0.1 * self.sz[0]
                self.pBar.setVert(i + self.lut.numEntry+1, v, False)
                v[0] = 0.0;
                self.pBar.setVert(i + (self.lut.numEntry+1)*2, v, False)
                continue # end of for i
        if self.showAlpha:
            for i in range(self.lut.numEntry):
                self.pBar.setColor(i, self.lut.entry[i][:3])
                dv = self.lut.entry[i][3]
                dv = 2*dv - dv*dv
                v[0] = v[1] = v[2] = dv
                self.pBar.setColor(i + self.lut.numEntry, v)
                continue # end of for i
        else:
            for i in range(self.lut.numEntry):
                self.pBar.setColor(i, self.lut.entry[i][:3])
                self.pBar.setColor(i + self.lut.numEntry, self.lut.entry[i][:3])
                continue # end of for i
        self.pBar.generateBbox()
        self.pBar.setBboxColor(self._colors[0])

        # title
        if self.direction == CMapBarDisp.CBD_HORIZONTAL:
            self.pTitleLbl.alignType = gfxNode.AL_LEFT
            self.pTitleLbl.trans((0.0, 0.7*self.sz[1]
                                  +CMapBarDisp.CBD_LABEL_SIZE*0.5, 0.0))
        else:
            self.pTitleLbl.alignType = gfxNode.AL_CENTER
            self.pTitleLbl.trans((0.45*self.sz[0],
                                  0.7*self.sz[1]
                                  +CMapBarDisp.CBD_LABEL_SIZE*0.5, 0.0))
        self.pTitleLbl.setColor(0, self._colors[0][:3])

        # labels
        n = self.pLbls.getNumChildren()
        if self.numLbls > n:
            for i in range(n, self.numLbls):
                pltxt = letters.Letters(name='CBD_label',
                                        localMaterial=False,
                                        font=letters.FONT_LINE)
                pltxt.setTransparency(True)
                self.pLbls.addChild(pltxt)
                continue # end of for i
        elif self.numLbls < n:
            for i in range(self.numLbls, n):
                pltxt = self.pLbls.getChild(i)
                try:
                    pltxt.setLetters("")
                except:
                    pass
                continue # end of for i
        dval = 0.0
        if self.numLbls > 1:
            dval = (self.lut.maxVal - self.lut.minVal) / (self.numLbls -1)
        fmt = "{:." + str(self.precLbls) + "f}"
        if self.direction == CMapBarDisp.CBD_HORIZONTAL:
            dv = (1.0 * self.sz[0] / (self.numLbls -1)) if (self.numLbls > 1) \
                else 0.0
            for i in range(self.numLbls):
                pltxt = self.pLbls.getChild(i)
                pltxt.alignType = gfxNode.AL_CENTER
                pltxt.setLetters(fmt.format(self.lut.minVal + dval*i))
                pltxt.identity()
                pltxt.trans((i * dv,
                             -CMapBarDisp.CBD_LABEL_SIZE*0.2, 0.0))
                pltxt.fontScale = CMapBarDisp.CBD_LABEL_SIZE
                pltxt.setColor(0, self._colors[0][:3])
                continue # end of for i
        else:
            dv = (0.7 * self.sz[1] / (self.numLbls -1)) if (self.numLbls > 1) \
                else 0.0
            for i in range(self.numLbls):
                pltxt = self.pLbls.getChild(i)
                pltxt.alignType = gfxNode.AL_LEFT
                pltxt.setLetters(fmt.format(self.lut.minVal + dval*i))
                pltxt.identity()
                pltxt.trans((0.5 * self.sz[0],
                             i*dv -CMapBarDisp.CBD_LABEL_SIZE*0.5, 0.0))
                pltxt.fontScale = CMapBarDisp.CBD_LABEL_SIZE
                pltxt.setColor(0, self._colors[0][:3])
                continue # end of for i

        return True
    
