#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from gfxNode import *
from utilMath import *
import math

#----------------------------------------------------------------------
"""プリミティブへの回転／スケール適用タイプ"""
(PRIMSET_ROT, PRIMSET_SCALE) = (0x1, 0x1<<1)

class PrimSet(GfxNode):
    """
    PrimSetクラスは，登録された形状データをプリミティブとし，自分の
    頂点座標位置に描画するシーングラフノードクラスです．
    登録されたプリミティブを，頂点集合として与えられた座標位置に描画します．
      _prim: プリミティブ
      _rsMode: プリミティブの回転／スケール適用フラグ
               (PRIMSET_ROT, PRIMSET_SCALE のコンビネーション)
    """
    def __init__(self, name =Node._NONAME, suicide =False):
        GfxNode.__init__(self, name, suicide)
        self._rsMode = PRIMSET_ROT|PRIMSET_SCALE
        self._prim = None

    def __del__(self):
        if self._prim:
            self._prim.remRef(self)
            self._prim = None
        GfxNode.__del__(self)

    def setPrimitive(self, prim):
        """
        プリミティブを登録する
        - prim: 登録するプリミティブ
        """
        if self._prim == prim: return
        if self._prim:
            self._prim.remRef(self)
        self._prim = prim
        if self._prim:
            self._prim.addRef(self)
        self.generateBbox()
        self.notice()
        return

    def getPrimitive(self):
        """
        登録されているプリミティブを返す
        """
        return self._prim

    def setRotScaleMode(self, rsm):
        """
        プリミティブの回転／スケール適用フラグを設定する
        - rsm: 回転／スケール適用フラグ
               PRIMSET_ROT: 描画する頂点に対応する法線ベクトルが存在する場合
                 (0, 0, 1)をその法線ベクトルに合致させる回転を適用してから
                 プリミティブを描画する
               PRIMSET_SCALE: 描画する頂点に対応する法線ベクトルが存在する場合
                 その法線ベクトルの長さをスケーリング倍率とする拡大縮小を
                 適用してからプリミティブを描画する
        """
        if self._rsMode == rsm: return
        self._rsMode = rsm
        self.notice()
        return

    def getRotScaleMode(self):
        """
        回転／スケール適用フラグを返す
        """
        return self._rsMode

    def calcBboxPoints(self, idx, xbb):
        """
        頂点毎のバウンディングボックス更新
        - idx: 頂点インデックス
        - xbb: 作業用バウンディングボックス領域
        """
        if idx < 0 or idx >= self.nVerts: return False
        if not self._prim: return False
        pbb = self._prim.getBbox()
        
        scFac = 1.0
        if (self._rsMode & PRIMSET_SCALE) and idx < self.nNormals:
            scFac = abs(Vec3(self._normals[idx]))
        
        xbb[0][0:3] = (Vec3(self._verts[idx]) + pbb[0]*scFac)[0:3]
        xbb[1][0:3] = (Vec3(self._verts[idx]) + pbb[1]*scFac)[0:3]
        return True

    def rumor(self, ref):
        """
        破壊通知を受けつける
        - ref: 破壊されたノード
        """
        if self._prim and self._prim == ref:
            self._prim = None
            self.notice()
            return
        Node.rumor(self, ref)
        return

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        if not self._prim:
            Node.generateBbox()
            return

        if self.nVerts < 1:
            self._bbox[0][:] = Vec3()[0:3]
            self._bbox[1][:] = self._bbox[0][:]
            self.checkBbox()
            return
        
        xbb = [Vec3(), Vec3()]
        if not self.calcBboxPoints(0, self._bbox):
            self._bbox[0][:] = self._verts[0][:]
            self._bbox[1][:] = self._bbox[0][:]
            
        for i in range(1, self.nVerts):
            if not self.calcBboxPoints(i, xbb):
                xbb[0][:] = self._verts[i][:]
                xbb[1][:] = xbb[0][:]
            if self._bbox[0][0] > xbb[0][0]: self._bbox[0][0] = xbb[0][0]
            if self._bbox[1][0] < xbb[1][0]: self._bbox[1][0] = xbb[1][0]
            if self._bbox[0][1] > xbb[0][1]: self._bbox[0][1] = xbb[0][1]
            if self._bbox[1][1] < xbb[1][1]: self._bbox[1][1] = xbb[1][1]
            if self._bbox[0][2] > xbb[0][2]: self._bbox[0][2] = xbb[0][2]
            if self._bbox[1][2] < xbb[1][2]: self._bbox[1][2] = xbb[1][2]
        self.checkBbox()
        return

    def callPrimRender(self, rt, pos, vec =None):
        """
        プリミティブのレンダリング関数呼び出し
        - rt: レンダリングモード
        - pos: レンダリング位置
        - vec: レンダリング姿勢・スケールベクトル
        """
        if not self._prim: return
        glPushMatrix()

        # ignore material and matrix of the primitive,
        # apply local transform
        glTranslatef(pos[0], pos[1], pos[2])
        if vec and self._rsMode:
            v = Vec3(vec)
            l = abs(v)
            if l < 1e-6: l = 1e-6
            v = v.unit()
            ang = math.acos(v[2])
            if (self._rsMode & PRIMSET_ROT) and (v[0] != 0.0 or v[1] != 0.0):
                glRotatef(Rad2Deg(ang), -v[1], v[0], 0.0)
            if (self._rsMode & PRIMSET_SCALE):
                glScalef(l, l, l)

        # call renderer of primitive
        if rt & (RT_SMOOTH | RT_NOLIGHT | RT_FLAT):
            self._prim.renderSolid()
        if rt & RT_WIRE:
            self._prim.renderWire()
        if rt & RT_POINT:
            self._prim.renderPoint()

        glPopMatrix()
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        プリミティブのrenderSolid()を呼び出す
        """
        if not self._prim: return
        for index in range(self.nVerts):
            if self._colorMode == AT_PER_VERTEX and index < self.nColors:
                glColor4fv(self._colors[index])
            if index < self.nNormals:
                self.callPrimRender(RT_SMOOTH,
                                    self._verts[index], self._normals[index])
            else:
                self.callPrimRender(RT_SMOOTH, self._verts[index])
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        プリミティブのrenderWire()を呼び出す
        """
        if not self._prim: return
        for index in range(self.nVerts):
            if not self._useAuxLineColor and \
                   self._colorMode == AT_PER_VERTEX and index < self.nColors:
                glColor4fv(self._colors[index])
            if index < self.nNormals:
                self.callPrimRender(RT_WIRE,
                                    self._verts[index], self._normals[index])
            else:
                self.callPrimRender(RT_WIRE, self._verts[index])
        return

    def renderPoint(self):
        """
        ポイントレンダリング
        プリミティブのrenderPoint()を呼び出す．プリミティブがNoneの場合は
        GfxNode.renderPoint()を呼び出す．
        """
        if self._prim:
            for index in range(self.nVerts):
                if not self._useAuxPointColor and \
                       self._colorMode == AT_PER_VERTEX and \
                       index < self.nColors:
                    glColor4fv(self._colors[index])
                if index < self.nNormals:
                    self.callPrimRender(RT_POINT,
                                        self._verts[index],
                                        self._normals[index])
                else:
                    self.callPrimRender(RT_POINT, self._verts[index])
        else:
            GfxNode.renderPoint(self)
        return

