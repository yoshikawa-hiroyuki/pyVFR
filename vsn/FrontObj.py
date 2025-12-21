#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""FrontObj implementation
  FrontObjクラス, FrontAxisクラスを提供します.
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *
from OpenGL.GL import *


#----------------------------------------------------------------------
# FrontObj class implementation

class FrontObj(gfxGroup.GfxGroup):
    """ FrontObjクラス
     FrontAxisの基底クラスです.
    """
    def __init__(self, **args):
        """ 初期設定.
        """
        gfxGroup.GfxGroup.__init__(self, **args)

    def setPosition(self, x, y):
        """ Positionを設定.
          x - float. x座標
          y - float. y座標
        """
        self.identity()
        self.trans((x, y, 0.0))

    def getPosition(self):
        """ Positionを取得.
          戻り値 -> Point. position.
        """
        return (self._matrix[12], self._matrix[13])

    def render_(self, transpMode):
        """ renderを実行.
          transpMode - bool. モード
        """
        vp = glGetIntegerv(GL_VIEWPORT)
        asp = 1.0
        if vp[2] > 0 and vp[3] > 0: asp = float(vp[2])/float(vp[3])
        glPushMatrix()
        glTranslatef(self._matrix[12]*(asp -1.0), 0.0, 0.0)
        gfxGroup.GfxGroup.render_(transpMode)
        glPopMatrix()
        return


#----------------------------------------------------------------------
# FrontAxis class implementation

class FrontAxis(FrontObj):
    """ FrontAxisクラス
    """
    __symW = 8
    __symH = 8
    __sym = (
        (0x81, 0xc2, 0x64, 0x38, 0x1c, 0x26, 0x43, 0x81),
        (0x18, 0x18, 0x18, 0x18, 0x1c, 0x26, 0x43, 0x81),
        (0xFF, 0x61, 0x30, 0x18, 0x0c, 0x06, 0x83, 0x7f))
    
    def __init__(self, **args):
        """ 初期設定.
        """
        FrontObj.__init__(self, **args)

        # axes arrow
        self.axes = vectors.Vectors()
        self.axes.alcData(nV = 3, nN = 3, nC = 3)
        self.axes.setVert(0, (0.0, 0.0, 0.0))
        self.axes.setVert(1, (0.0, 0.0, 0.0))
        self.axes.setVert(2, (0.0, 0.0, 0.0))
        self.axes.setNormal(0, (0.1, 0.0, 0.0))
        self.axes.setNormal(1, (0.0, 0.1, 0.0))
        self.axes.setNormal(2, (0.0, 0.0, 0.1))
        self.axes.setColor(0, (1.0, 0.0, 0.0, 1.0))
        self.axes.setColor(1, (0.0, 1.0, 0.0, 1.0))
        self.axes.setColor(2, (0.0, 0.0, 1.0, 1.0))
        self.axes._colorMode = gfxNode.AT_PER_VERTEX
        self.addChild(self.axes)

        # initiali pos of left-bottom corner
        self.trans((-0.9, -0.9, 0.0))

    def setRotMatrix(self, rotMat):
        """ Matrixを設定.
          rotMat - Matrix. matrix値
        """
        M = utilMath.Mat4(rotMat)
        M[12] = -0.9
        M[13] = -0.9
        M[14] = 0.0
        self.setMatrix(M)

    def render_(self, transpMode):
        """ renderを実行.
          transpMode - bool. 透過モード.
                       True:axes labelを表示する, False:しない.
        """
        vp = glGetIntegerv(GL_VIEWPORT)
        asp = 1.0
        if vp[2] > 0 and vp[3] > 0: asp = float(vp[2])/float(vp[3])
        glPushMatrix()
        glTranslatef(self._matrix[12]*(asp -1.0), 0.0, 0.0)

        # draw myself
        gfxGroup.GfxGroup.render_(self, transpMode)

        # draw axes label
        if self._renderMode != gfxNode.RT_NONE and \
               transpMode == self._transparent :
            glDisable(GL_LIGHTING)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glColor4fv(self._colors[0])
            glMultMatrixf(self._matrix.m_v.tolist())
            glRasterPos3f(0.1, 0.0, 0.0)
            glBitmap(FrontAxis.__symW, FrontAxis.__symH,
                     0.0, 0.0, 0.0, 0.0, FrontAxis.__sym[0])
            glRasterPos3f(0.0, 0.1, 0.0)
            glBitmap(FrontAxis.__symW, FrontAxis.__symH,
                     0.0, 0.0, 0.0, 0.0, FrontAxis.__sym[1])
            glRasterPos3f(0.0, 0.0, 0.1)
            glBitmap(FrontAxis.__symW, FrontAxis.__symH,
                     0.0, 0.0, 0.0, 0.0, FrontAxis.__sym[2])
            glEnable(GL_LIGHTING)
        
        glPopMatrix()
        return
