#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""

#----------------------------------------------------------------------
import numpy as N
import ctypes as C
import os.path
vfr_impl = N.ctypeslib.load_library('vfr_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))
vfr_impl.gfxNode_DrawPoints.restype = C.c_int
vfr_impl.gfxNode_DrawPoints.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]

vfr_impl.gfxNode_DrawLines.restype = C.c_int
vfr_impl.gfxNode_DrawLines.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]

vfr_impl.gfxNode_DrawLineStrip.restype = C.c_int
vfr_impl.gfxNode_DrawLineStrip.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int, C.c_int]


#----------------------------------------------------------------------
from .gfxNode import *
from .utilMath import *

class Lines(GfxNode):
    """
    線分集合クラス
    Linesクラスは、線分集合を描画するシーングラフノードクラスです．
    与えられた頂点集合を 2つづつ線分として描画を行います．
    頂点数が奇数個の場合、最後の1つは無視されます．
    """

    def __init__(self, name =Node._NONAME, suicide =False):
        GfxNode.__init__(self, name, suicide)
        self._renderMode = RT_WIRE

    def renderFeedBack(self, tgt):
        """
        フィードバックテストのためのレンダリングを行います.
        指定されたターゲットIDが自分自身のID番号と異なる場合は何もしません．
        フィードバックテストモード(_feedbackMode)の値に応じ以下の動作をします．
        FB_VERTEX
          登録されている頂点順に0から付番された番号でフィードバックテストの
          結果を返す.
          頂点数が奇数個の場合の最後の頂点も、フィードバックテストの対象となる.
        FB_EDGE
          描画される順序で線分に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_FACE
          フィードバックテストは常に合格数 0 を返す.
        - tgt: フィードバックターゲットノードのID
        """
        if not self._id == tgt:
            return

        self.applyMatrix()
        glDisable(GL_LIGHTING)

        if self._feedbackMode == FB_VERTEX:
            # call gfxNode_DrawPoints
            if self.nVerts > 0:
                ret = vfr_impl.gfxNode_DrawPoints(self.nVerts, self._verts,
                                                  0, None, 0, 1)
                if ret == 0: pass
        elif self._feedbackMode == FB_EDGE:
            # call gfxNode_DrawLines
            if self.nVerts > 0:
                nv = self.nVerts
                ret = vfr_impl.gfxNode_DrawLines(self.nVerts, self._verts,
                                                 0, None, 0, 1)
                if ret == 0: pass
        else:
            # do nothing.
            pass

        glEnable(GL_LIGHTING)
        self.unApplyMatrix()
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        if self.nVerts < 2 :
            return

        # display-list check
        if self.beginDispList(DLF_WIRE): return

        # draw lines via gfxNode_DrawLines
        nv = self.nVerts
        vtx = self._verts
        if self._colorMode == AT_WHOLE or self._useAuxLineColor:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors
        ret = vfr_impl.gfxNode_DrawLines(nv, vtx,  nc, col,
                                         self._colorMode, 0)
        if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_WIRE)
        return


#----------------------------------------------------------------------
class LineStrip(GfxNode):
    """
    連結線分クラス
    LinesStripクラスは、連結線分を描画するシーングラフノードクラスです．
    与えられた頂点集合を順に直線で連結して描画を行います．
    ループモードがTRUEの場合は、先頭の頂点と最後の頂点を連結し、閉多角形を
    描画します．
      loopMode: ループモード
    """

    def __init__(self, name =Node._NONAME, suicide =False, loop =False):
        GfxNode.__init__(self, name, suicide)
        self._renderMode = RT_WIRE
        self.loopMode = loop

    def renderFeedBack(self, tgt):
        """
        フィードバックテストのためのレンダリングを行います.
        指定されたターゲットIDが自分自身のID番号と異なる場合は何もしません．
        フィードバックテストモード(_feedbackMode)の値に応じ以下の動作をします．
        FB_VERTEX
          登録されている頂点順に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_EDGE
          描画される順序で線分に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_FACE
          フィードバックテストは常に合格数 0 を返す.
        - tgt: フィードバックターゲットノードのID
        """
        if not self._id == tgt:
            return

        self.applyMatrix()
        glDisable(GL_LIGHTING)

        if self._feedbackMode == FB_VERTEX:
            # call gfxNode_DrawPoints
            if self.nVerts > 0:
                ret = vfr_impl.gfxNode_DrawPoints(self.nVerts, self._verts,
                                                  0, None,  0, 1)
                if ret == 0: pass
        elif self._feedbackMode == FB_EDGE:
            # call gfxNode_DrawLineStrip
            if self.nVerts > 0:
                ret = vfr_impl.gfxNode_DrawLineStrip(self.nVerts, self._verts,
                                                     0, None, 0,
                                                     self.loopMode, 1)
                if ret == 0: pass
        else:
            # do nothing.
            pass

        glEnable(GL_LIGHTING)
        self.unApplyMatrix()
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        if self.nVerts < 2 :
            return

        # display-list check
        if self.beginDispList(DLF_WIRE): return

        # draw lines via gfxNode_DrawLineStrip
        nv = self.nVerts
        vtx = self._verts
        if self._colorMode == AT_WHOLE or self._useAuxLineColor:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors
        ret = vfr_impl.gfxNode_DrawLineStrip(nv, vtx,  nc, col,
                                             self._colorMode,
                                             self.loopMode, 0)
        if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_WIRE)
        return
