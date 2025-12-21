#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import math
from OpenGL.GL import *
from .gfxNode import *


#----------------------------------------------------------------------
"""光源タイプ"""
(LT_DIRECTIONAL, LT_POINT, LT_SPOT) = range(3)

class Light(GfxNode):
    """
    ライティング・ノードクラス
    Lightクラスは、光源(ライト)を表すシーングラフノードクラスです．
    このクラスはSceneクラスによってインスタンスが作成され，シーングラフに
    接続されます．
      _on: ライトのON/OFFフラグ
      _lightType: 光源タイプ
      _showLight: ライトの表示モード
      _order: OpenGL光源番号
      _diffuse: 散乱光強度(RGBA)
      _ambient: 環境光強度(RGBA)
      _specular: ハイライト光強度(RGBA)
      _spotCutoff: スポットライトカットオフ角度(degree)
    """
    __lightOrder = {0:GL_LIGHT0, 1:GL_LIGHT1, 2:GL_LIGHT2, 3:GL_LIGHT3}
    __positionPara = [0.0, 0.0, 1.0, 0.0]
    __positionPoint = [0.0, 0.0, 0.0, 1.0]
    __directionSpot = [0.0, 0.0, -1.0]
    __cutoffPoint = 180.0
    
    def __init__(self, order, **args):
        GfxNode.__init__(self, **args)
        self.makeLight(order)
        return

    def makeLight(self, order):
        """
        ライティング属性の初期化
        各属性値を初期化します．
        - order: OpenGL光源番号
        """
        self._order = order
        self._diffuse = [1.0, 1.0, 1.0, 1.0]
        self._ambient = [0.2, 0.2, 0.2, 1.0]
        self._specular = [1.0, 1.0, 1.0, 1.0]
        self._spotCutoff = [45.0 ]
        self._on = False
        self._lightType = LT_DIRECTIONAL
        self._showLight = False
        return

    def render(self):
        """
        ライティングのOpenGL適用
        設定された属性に応じ，OpenGLのライティング設定コマンドを実行します．
        更に，drawLight()の実行も行います．
        """
        try:
            l = Light.__lightOrder[self._order]
        except:
            return
        if self._on:
            glEnable(l)
        else:
            glDisable(l)
        
        self.applyMatrix()

        glLightfv(l, GL_AMBIENT, self._ambient)
        glLightfv(l, GL_DIFFUSE, self._diffuse)
        glLightfv(l, GL_SPECULAR, self._specular)

        if self._lightType == LT_POINT:
            glLightfv(l, GL_POSITION, Light.__positionPoint)
            glLightfv(l, GL_SPOT_CUTOFF, Light.__cutoffPoint)
        elif self._lightType == LT_SPOT:
            glLightfv(l, GL_POSITION, Light.__positionPoint)
            glLightfv(l, GL_SPOT_CUTOFF, self._spotCutoff)
            glLightfv(l, GL_SPOT_DIRECTION, Light.__directionSpot)
        else:
            glLightfv(l, GL_POSITION, Light.__positionPara)

        self.drawLight()

        self.unApplyMatrix()
        return

    def drawLight(self):
        """
        ライトシンボルのOpenGL描画
        _showLightがTrueの場合に，ライトのシンボルをOpenGLで描画します．
        """
        if not self._showLight: return

        if self._pickable & PT_OBJECT:
            glPushName(self._id)

        self.applyMaterial()

        glDisable(GL_LIGHTING)
        glColor4fv(self._diffuse)

        if not self.beginDispList(DLF_WIRE):
            
            if self._lightType == LT_POINT:
                glBegin(GL_LINES)
                glVertex3f(-1.0, 0.0, 0.0)
                glVertex3f( 1.0, 0.0, 0.0)
                glEnd()
                glBegin(GL_LINES)
                glVertex3f(0.0,-1.0, 0.0)
                glVertex3f(0.0, 1.0, 0.0)
                glEnd()
                glBegin(GL_LINES)
                glVertex3f(0.0, 0.0,-1.0)
                glVertex3f(0.0, 0.0, 1.0)
                glEnd()
            elif self._lightType == LT_SPOT:
                glBegin(GL_LINES)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3fv(Light.__directionSpot)
                glEnd()
                ssc = math.sin(self._spotCutoff[0] * 0.017453293)
                csc = math.cos(self._spotCutoff[0] * 0.017453293)
                glBegin(GL_LINE_STRIP)
                glVertex3f(ssc, 0.0, -csc)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(-ssc, 0.0, -csc)
                glEnd()
                glBegin(GL_LINE_STRIP)
                glVertex3f(0.0, ssc, -csc)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(0.0, -ssc, -csc)
                glEnd()
            else:
                glBegin(GL_LINES)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex4fv(Light.__positionPara)
                glEnd()

            self.endDispList(DLF_WIRE)

        glEnable(GL_LIGHTING)
        self.unApplyMaterial()

        if self._pickable & PT_OBJECT:
            if not self._pickable & PT_BBOX:
                glLoadName(0)
        self.drawBbox()
                    
        if self._pickable & PT_OBJECT:
            glPopName()
        return

    def generateBbox(self):
        """
        バウンディングボックスの再計算
        Lightクラスのバウンディングボックは，常に[-1,-1,-1],[1,1,1]です．
        """
        self._bbox[0][0:] = (-1.0, -1.0, -1.0)
        self._bbox[1][0:] = (1.0, 1.0, 1.0)
        return

