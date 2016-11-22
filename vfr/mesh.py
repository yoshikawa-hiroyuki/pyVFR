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
vfr_impl.gfxMesh2D_DrawMeshFace.restype = C.c_int
vfr_impl.gfxMesh2D_DrawMeshFace.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int, C.c_int, C.c_int, C.c_int]

vfr_impl.gfxMesh2D_DrawMeshEdge.restype = C.c_int
vfr_impl.gfxMesh2D_DrawMeshEdge.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int, C.c_int, C.c_int]

vfr_impl.gfxMesh2D_CalcNormals.restype = C.c_int
vfr_impl.gfxMesh2D_CalcNormals.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.c_int, C.c_int]

vfr_impl.gfxNode_DrawPoints.restype = C.c_int
vfr_impl.gfxNode_DrawPoints.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]

#----------------------------------------------------------------------
from gfxNode import *
from utilMath import *

class Mesh2D(GfxNode):
    """
    2Dメッシュクラス
    Mesh2Dクラスは，2次元のメッシュを表現するシーングラフノードクラスです．
    指定されたサイズがM×Nの場合，与えられた頂点集合を(M×N)の格子配列とみなし，
    4格子点で構成される四角形を(M-1)×(N-1)個描画します．
    Mesh2Dクラスは非直交不等間隔格子(Irregular Mesh)であり，各頂点には3次元の
    座標が指定できます．
      meshSize: 格子サイズ(Point2クラス)
    """
    def __init__(self, name =Node._NONAME, suicide =False,
                 m =0, n =0):
        GfxNode.__init__(self, name, suicide)
        self.meshSize = Point2()
        self.setMeshSize(m, n);
        self.alcData(nN = 1)

    def setMeshSize(self, m, n):
        """
        メッシュサイズを設定します． 
        指定されたサイズの頂点が確保され，成功するとTrueを返します． 
        サイズが 2×2 よりも小さい場合，0×0 に設定されます．
        - m: メッシュサイズ(M方向)
        - n: メッシュサイズ(N方向)
        """
        ns = Point2(m, n);
        if self.meshSize == ns: return True
        total = ns.x * ns.y
        try:
            self.alcData(nV = total)
        except:
            return False
        self.meshSize = ns
        self.notice()
        return True

    def renderFeedBack(self, tgt):
        """
        フィードバックテストのためのレンダリングを行います.
        指定されたターゲットIDが自分自身のID番号と異なる場合は何もしません．
        フィードバックテストモード(_feedbackMode)の値に応じ以下の動作をします．
        FB_VERTEX
          登録されている頂点順に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_FACE
          面に0から(M-1)×(N-1)-1まで付番された番号でフィードバックテストの
          結果を返す.
        FB_EDGE
          エッジ(辺)に0から付番された番号でフィードバックテストの結果を返す.
          横線の辺番号は0〜(M-1)×N-1，縦線の辺番号は(M-1)×N〜(M-1)×N+M×(N-1)-1
          である．
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
            glPolygonMode(self._faceMode, GL_FILL);
            # call gfxMesh2D_DrawMeshFace
            if self.nVerts > 0:
                ret = vfr_impl.gfxMesh2D_DrawMeshFace(self.nVerts, self._verts,
                                                      0, None, 0, None,
                                                      self.meshSize.x,
                                                      self.meshSize.y,
                                                      0, 0, 1)
                if ret == 0: pass
        elif self._feedbackMode == FB_EDGE:
            # call gfxMesh2D_DrawMeshEdge
            if self.nVerts > 0:
                ret = vfr_impl.gfxMesh2D_DrawMeshEdge(self.nVerts, self._verts,
                                                      0, None,
                                                      self.meshSize.x,
                                                      self.meshSize.y,
                                                      0, 1)
                if ret == 0: pass
        else:
            pass

        glEnable(GL_LIGHTING)

        # un-apply matrix
        self.unApplyMatrix()
        return

    def generateNormals(self):
        """
        法線ベクトル再計算
        法線ベクトルタイプに応じ，法線ベクトルが確保され自動計算されます．
        成功するとTrueを返します．
        """
        nVerts = self.getNumVerts()
        if self.meshSize.x < 2 or self.meshSize.y < 2: return False
        if nVerts < self.meshSize.x * self.meshSize.y: return False;
        
        if self._normalMode == AT_WHOLE:
            self.alcData(nN = 1)
            v1, v2 = Vec3(), Vec3()
            x = vec3(self._verts[nVerts -1]) - Vec3(self._verts[0])
            v1.m_v[0:] = x[0:]
            x = Vec3(self._verts[self.meshSize.x -1]) \
                - Vec3(self._verts[self.meshSize.x * (self.meshSize.y -1)])
            v2.m_v[0:] = x[0:]
            vn = v1.cross(v2).unit()
            self._normals[0][0:] = vn[0:]
            self.notice()
            return True

        # allocate normals
        if self._normalMode == AT_PER_FACE:
            nmlNum = (self.meshSize.x-1) * (self.meshSize.y-1)
        else:
            nmlNum = self.meshSize.x * self.meshSize.y
        try:
            self.alcData(nN = nmlNum)
        except:
            return False
        
        # call gfxMesh2D_CalcNormals
        ret = vfr_impl.gfxMesh2D_CalcNormals(self.nVerts, self._verts,
                                             nmlNum, self._normals,
                                             self.meshSize.x, self.meshSize.y,
                                             self._normalMode)
        print "ret = ", ret
        if ret == 0: return False
        self.notice()
        return True

    def getFeedbackSize(self):
        """
        フィードバックサイズファクターを返す
        フィードバックテスト結果格納に必要なサイズを算出するための基準値を
        返します．
        """
        fsz = self.nVerts * GfxNode.FEEDBACK_SIZE_FACTOR
        if self._feedbackMode == FB_FACE:
            fsz = fsz * 4
        elif self._feedbackMode == FB_EDGE:
            fsz = fsz * 2
        return fsz

    def renderSolid(self):
        """
        ソリッドレンダリング
        ポリゴンでOpenGLによるレンダリングを行います．
        """
        if self.meshSize.x < 2 or self.meshSize.y < 2: return

        # display-list check
        if self.beginDispList(DLF_SOLID): return

        if self.nNormals > 0 and self._normalMode == AT_WHOLE:
            glNormal3fv(self._normals[0])

        # draw mesh via gfxMesh2D_DrawMeshFace
        if self.nVerts > 0:
            ret = vfr_impl.gfxMesh2D_DrawMeshFace(self.nVerts, self._verts,
                                                  self.nNormals, self._normals,
                                                  self.nColors, self._colors,
                                                  self.meshSize.x,
                                                  self.meshSize.y,
                                                  self._normalMode,
                                                  self._colorMode, 0)
            if ret == 0: print 'draw failed'

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        ワイヤーフレームでOpenGLによるレンダリングを行います．
        """
        if self.meshSize.x < 2 or self.meshSize.y < 2: return

        # display-list check
        if self.beginDispList(DLF_WIRE): return

        if self._colorMode == AT_WHOLE or self._useAuxLineColor:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors

        # draw mesh via gfxMesh2D_DrawMeshEdge
        if self.nVerts > 0:
            ret = vfr_impl.gfxMesh2D_DrawMeshEdge(self.nVerts, self._verts,
                                                  nc, col,
                                                  self.meshSize.x,
                                                  self.meshSize.y,
                                                  self._colorMode, 0)
            if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_WIRE)
        return
