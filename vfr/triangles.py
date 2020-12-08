#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .gfxNode import *
from .utilMath import *
import numpy as N
import ctypes as C


#----------------------------------------------------------------------
import os.path
vfr_impl = N.ctypeslib.load_library('vfr_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))
vfr_impl.gfxNode_DrawPoints.restype = C.c_int
vfr_impl.gfxNode_DrawPoints.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]
vfr_impl.gfxTriangles_DrawTrias.restype = C.c_int
vfr_impl.gfxTriangles_DrawTrias.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int, C.c_int]
vfr_impl.gfxTriangles_CalcNormals.restype = C.c_int
vfr_impl.gfxTriangles_CalcNormals.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*3), C.c_int]


#----------------------------------------------------------------------
class Triangles(GfxNode):
    """
    トライアングルセット・ノードクラス
    Trianglesクラスは，三角形集合を表示するシーングラフノードクラスです．
    与えられた頂点集合を3個づつに区切り，三角形をOpenGLで描画します．
    頂点数が3の倍数でない場合，最後の1ないし2個の頂点は無視されます．
    ただしレンダリングモードがRT_POINTの場合，頂点数が3の倍数でなくとも
    登録されている全ての頂点をポイントレンダリングします．
    """
    def __init__(self, name =Node._NONAME, suicide =False):
        GfxNode.__init__(self, name, suicide)

    def renderFeedBack(self, tgt):
        """
        フィードバックテスト用レンダリング
        指定ターゲットが自分の場合，フィードバックテストのためのレンダリングを
        行います.
        フィードバックテストにおいて，Trianglesノードはフィードバックモードに
        応じ，以下のような結果を返します．
         FB_VERTEX
          登録されている頂点順に0から付番された番号でフィードバックテストの
          結果を返す
         FB_FACE
          描画される順序でポリゴンに0から付番された番号でフィードバックテストの
          結果を返す
         FB_EDGE
          フィードバックテストは常に合格数0を返す
        - tgt: フィードバックターゲットノードのID
        """
        if not self._id == tgt:
            return

        # transformation matrix
        self.applyMatrix()

        glDisable(GL_LIGHTING)

        if self._feedbackMode == FB_VERTEX:
            # call gfxNode_DrawPoints
            if self.nVerts > 0:
                ret = vfr_impl.gfxNode_DrawPoints(self.nVerts, self._verts,
                                                  0, None,  0, 1)
                if ret == 0: pass
        elif self._feedbackMode == FB_FACE:
            # call gfxNode_DrawPoints
            if self.nVerts > 0:
                ret = vfr_impl.gfxTriangles_DrawTrias(self.nVerts, self._verts,
                                                      0,None, 0,None,  0, 0, 1)
                if ret == 0: pass
        else:
            # do nothing.
            pass

        glEnable(GL_LIGHTING)
        self.unApplyMatrix()
        return

    def generateNormals(self):
        """
        法線ベクトル再計算
        法線ベクトルタイプに応じ，法線ベクトルを確保し自動計算します．
        成功するとTrueを返します．(頂点数 < 3) の場合は何も実行しません．
        """
        numFace = self.getNumVerts() / 3
        if self._normalMode == AT_PER_VERTEX:
            numFace = self.getNumVerts()
        else:
            self._normalMode = AT_PER_FACE
        if numFace < 1: return False

        # Allocate Normals' area
        self.alcData(nN = numFace)

        # Calc normals by gfxTriangles_CalcNormals
        ret = vfr_impl.gfxTriangles_CalcNormals(self.nVerts, self._verts,
                                                self.nNormals, self._normals,
                                                self._normalMode)
        if ret == 0: pass

        self.notice()
        return (ret != 0)

    def renderSolid(self):
        """
        ソリッドレンダリング
        ソリッドモード(面塗りつぶし)でOpenGLによるレンダリングを行います．
        """
        if self.nVerts < 3: return

        # display-list check
        if self.beginDispList(DLF_SOLID): return

        if self.nNormals > 0 and self._normalMode == AT_WHOLE:
            glNormal3fv(self._normals[0])
        
        # draw trias via gfxTriangles_DrawTrias
        nv = self.nVerts
        vtx = self._verts
        if self._normalMode == AT_WHOLE:
            nn = 0
            nml = None
        else:
            nn = self.nNormals
            nml = self._normals
        if self._colorMode == AT_WHOLE:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors
        ret = vfr_impl.gfxTriangles_DrawTrias(nv, vtx,  nn, nml,  nc, col,
                                              self._normalMode,
                                              self._colorMode, 0)
        if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        ワイヤーフレームモードでOpenGLによるレンダリングを行います．
        """
        self.renderSolid()
