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
vfr_impl.gfxVectors_DrawVectors.restype = C.c_int
vfr_impl.gfxVectors_DrawVectors.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_float, C.c_int, C.c_int,
    C.c_int, C.c_float, C.c_float, C.c_int]

vfr_impl.gfxNode_DrawPoints.restype = C.c_int
vfr_impl.gfxNode_DrawPoints.argtypes = [
    C.c_int, C.POINTER(C.c_float*3),
    C.c_int, C.POINTER(C.c_float*4),
    C.c_int, C.c_int]


#----------------------------------------------------------------------
from gfxNode import *

"""ベクトルポジションタイプ"""
(VECPOS_NORMAL, VECPOS_CENTER, VECPOS_TIP) = range(3)


class Vectors(GfxNode):
    """
    ベクトル集合クラス
    Vectorsクラスは、ベクトル集合を描画するシーングラフノードクラスです．
    与えられた頂点位置に 法線ベクトルとして与えられたベクトルデータを矢印として
    描画します．
    矢印の大きさは、法線ベクトルの長さにスケーリングファクターを掛けたものに
    なります．
      showHead: アローヘッド表示モード
      posType: ベクトル表示位置タイプ(VECPOS_NORMAL, VECPOS_CENTER, VECPOS_TIP)
      headScale: アローヘッドの長さの、全体の長さに対する割合
      headWidth: アローヘッドの幅の、全体の長さに対する割合
      scaleFactor: 矢印の長さの、実際の長さに対するスケーリングファクター
      showZero: 長さが0のベクトルを(点で)表示するかどうか
    """

    def __init__(self, name =Node._NONAME, suicide =False):
        GfxNode.__init__(self, name, suicide)
	self._renderMode = RT_WIRE
        self.showHead = True
        self.posType = VECPOS_NORMAL
        self.headScale = 0.2
        self.headWidth = 0.05
        self.scaleFactor = 1.0
        self.showZero = True

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        if self.nVerts < 1 or self.nNormals < 1 :
            return

        # display-list check
        if self.beginDispList(DLF_WIRE): return

        # draw vectors via gfxVectors_DrawVectors
        nv = self.nVerts
        vtx = self._verts
        nn = self.nNormals
        nml = self._normals
        if self._colorMode == AT_WHOLE or self._useAuxLineColor:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors
        showZ, showH = 0, 0
        if self.showZero: showZ = 1
        if self.showHead: showH = 1
        ret = vfr_impl.gfxVectors_DrawVectors(nv, vtx,  nn, nml,  nc, col,
                                              self.scaleFactor, showZ,
                                              self.posType, showH,
                                              self.headScale, self.headWidth,
                                              0)
        if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_WIRE)
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
          描画される順序で線分に0から付番された番号でフィードバックテストの
          結果を返す.
        FB_FACE
          フィードバックテストは常に合格数 0 を返す.
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
        elif self._feedbackMode == FB_EDGE:
            # call gfxVectors_DrawVectors
            if self.nVerts > 0 and self.nNormals > 0:
                nv = self.nVerts
                vtx = self._verts
                nn = self.nNormals
                nml = self._normals
                ret = vfr_impl.gfxVectors_DrawVectors(nv,vtx, nn,nml, 0,None,
                                                      self.scaleFactor, 0,
                                                      self.posType, 0,
                                                      0.0, 0.0, 1)
                if ret == 0: pass
        else:
            # do nothing.
            pass

        glEnable(GL_LIGHTING)

        # un-apply matrix
        self.unApplyMatrix()
        return


#----------------------------------------------------------------------
def ReadPwn(path):
    """
    PWNファイルを入力し，対応するVectorsクラスのインスタンスを生成し，
    返す関数です．
    - path: PWN(Points With Normals)形式のファイルのパス
    """
    vecNode = None
    nv = 0
    try:
        f = open(path, 'r')
    except:
        return vecNode

    # read nv
    for line in f:
        if len(line) < 1 or line[0] == '#':
            continue
        cols = line.split()
        nv = int(cols[0])
        break
    if nv < 1:
        return vecNode

    # allocate
    try:
        vecNode = Vectors()
        vecNode.alcData(nV = nv, nN = nv)
    except:
        return None

    # read coordinates
    idx = 0
    for line in f:
        if len(line) < 1 or line[0] == '#':
            continue
        cols = line.split()
        vecNode._verts[idx][0] = float(cols[0])
        vecNode._verts[idx][1] = float(cols[1])
        vecNode._verts[idx][2] = float(cols[2])
        idx = idx + 1
        if idx >= nv: break

    # read normals
    idx = 0
    for line in f:
        if len(line) < 1 or line[0] == '#':
            continue
        cols = line.split()
        vecNode._normals[idx][0] = float(cols[0])
        vecNode._normals[idx][1] = float(cols[1])
        vecNode._normals[idx][2] = float(cols[2])
        idx = idx + 1
        if idx >= nv: break

    f.close()

    vecNode._normalMode = AT_PER_VERTEX
    vecNode.generateBbox()
    return vecNode
