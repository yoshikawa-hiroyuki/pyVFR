#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) YoH, 2026, All Right Reserved.

"""

import sys, os
import numpy as np
import ctypes as C
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr.gfxNode import *

#----------------------------------------------------------------------
vsn_impl = np.ctypeslib.load_library('vsn_impl',
                                     os.path.join(os.path.dirname(__file__),
                                                  "lib"))
vsn_impl.VsnDrawPointSet.restype = C.c_int
vsn_impl.VsnDrawPointSet.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int]

vsn_impl.VsnDrawLineStripSet.restype = C.c_int
vsn_impl.VsnDrawLineStripSet.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]

#----------------------------------------------------------------------
class vsnLineStripSet(GfxNode):
    """
    連結線分集合クラス
    LinesStripSetクラスは、複数の連結線分を描画するシーングラフノードクラスです．
    与えられた頂点集合を順に直線で連結して描画を行います．
    各連結線分の頂点数は、インデックス配列の値を参照します．インデックス配列が空の
    場合は、連結線分は描画されません.
    ループモードがTRUEの場合は、各連結線分の先頭の頂点と最後の頂点を連結し、
    閉多角形を描画します．
      loopMode: ループモード
    """

    def __init__(self, **args):
        """
        args: loop =False
        """
        GfxNode.__init__(self, **args)
        self._renderMode = RT_WIRE
        self.loopMode = False if not 'loop' in args else args['loop']
        return

    def renderFeedBack(self, tgt):
        """
        フィードバックテストのためのレンダリングを行います.
        指定されたターゲットIDが自分自身のID番号と異なる場合は何もしません．
        フィードバックテストモード(_feedbackMode)の値に応じ以下の動作をします．
        FB_VERTEX
          登録されている頂点順に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_EDGE
          描画される順序で連結線分に0から付番された番号でフィードバックテストの
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
            # call VsnDrawPointSet
            if self.nVerts > 0:
                ret = vsn_impl.VsnDrawPointSet(self.nVerts, self._verts,
                                               0, None,  1)
                if ret == 0: pass
        elif self._feedbackMode == FB_EDGE:
            # call DrawLineStripSet (not feedback mode)
            vidx = 0
            for i in range(self.nIndices):
                if self._indices[i] < 2:
                    continue
                idcxol = id_to_rgba(i)
                glColor4fv(idcxol)
                ret = vsn_impl.VsnDrawLineStripSet(self._indices[i],
                                                   C.byref(self._verts[vidx]),
                                                   0, None,  0,
                                                   self.loopMode, 0)
                if ret == 0: pass
                vidx += self._indices[i]
                continue # end of for(i)
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
        if self.nVerts < 2 or self.nIndices < 1:
            return

        # display-list check
        if self.beginDispList(DLF_WIRE):
            return

        # default color args
        if self._useAuxLineColor or \
           self._colorMode == AT_WHOLE or self._colorMode == AT_PER_FACE:
            nc = 0
            col = None

        # draw linestrips via VsnDrawLineStripSet
        vidx = 0
        for i in range(self.nIndices):
            if self._indices[i] < 2 or vidx + self._indices[i] > self.nVerts:
                continue

            if not self._useAuxLineColor:
                if self._colorMode == AT_PER_FACE:
                    if i < self.nColors:
                        glColor4fv(self._colors[i])
                elif self._colorMode == AT_PER_VERTEX:
                    if vidx + self._indices[i] <= self.nColors:
                        nc = self._indices[i]
                        col = C.byref(self._colors[vidx])
                    else:
                        nc = 0
                        col = None
            
            ret = vsn_impl.VsnDrawLineStripSet(self._indices[i],
                                               C.byref(self._verts[vidx]),
                                               nc, col,
                                               self.loopMode, 0)
            if ret == 0: pass
            vidx += self._indices[i]
            continue # end of for(i)

        # end display-list definition
        self.endDispList(DLF_WIRE)
        return
