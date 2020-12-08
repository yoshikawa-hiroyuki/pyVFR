#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .gfxNode import *
from .utilMath import *

#----------------------------------------------------------------------
class Cube(GfxNode):
    """
    直方体クラス
    Cubeクラスは，直方体を表すシーングラフノードクラスです．
    指定された幅(width)、高さ(height)、奥行き(depth)に対し，中心を
    ローカル座標系の原点とする直方体をレンダリングします．
      width: 幅
      height: 高さ
      depth: 奥行き
    """
    def __init__(self, name =Node._NONAME, suicide =False,
                 width=1.0, height=1.0, depth=1.0):
        GfxNode.__init__(self, name, suicide)
        self.width = width
        self.height = height
        self.depth = depth
        self.alcData(nV=1)
        self._verts[0][:] = (0, 0, 0)
        self.generateBbox()

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        self._bbox[0][0] = -self.width*0.5
        self._bbox[1][0] =  self.width*0.5
        self._bbox[0][1] = -self.height*0.5
        self._bbox[1][1] =  self.height*0.5
        self._bbox[0][2] = -self.depth*0.5
        self._bbox[1][2] =  self.depth*0.5

    def renderSolid(self):
        """
        ソリッドレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # draw
        hW = 0.5 * self.width
        hH = 0.5 * self.height
        hD = 0.5 * self.depth
        
        glNormal3f(1.0, 0.0, 0.0)
        glBegin(GL_POLYGON)
        glVertex3f( hW, -hH, -hD)
        glVertex3f( hW,  hH, -hD)
        glVertex3f( hW,  hH,  hD)
        glVertex3f( hW, -hH,  hD)
        glEnd()
        glNormal3f(-1.0, 0.0, 0.0)
        glBegin(GL_POLYGON)
        glVertex3f(-hW, -hH, -hD)
        glVertex3f(-hW, -hH,  hD)
        glVertex3f(-hW,  hH,  hD)
        glVertex3f(-hW,  hH, -hD)
        glEnd()
        glNormal3f(0.0, 1.0, 0.0)
        glBegin(GL_POLYGON)
        glVertex3f(-hW,  hH, -hD)
        glVertex3f(-hW,  hH,  hD)
        glVertex3f( hW,  hH,  hD)
        glVertex3f( hW,  hH, -hD)
        glEnd()
        glNormal3f(0.0, -1.0, 0.0)
        glBegin(GL_POLYGON)
        glVertex3f(-hW, -hH, -hD)
        glVertex3f( hW, -hH, -hD)
        glVertex3f( hW, -hH,  hD)
        glVertex3f(-hW, -hH,  hD)
        glEnd()
        glNormal3f(0.0, 0.0, 1.0)
        glBegin(GL_POLYGON)
        glVertex3f( hW,  hH,  hD)
        glVertex3f(-hW,  hH,  hD)
        glVertex3f(-hW, -hH,  hD)
        glVertex3f( hW, -hH,  hD)
        glEnd()
        glNormal3f(0.0, 0.0, -1.0)
        glBegin(GL_POLYGON)
        glVertex3f( hW, -hH, -hD)
        glVertex3f(-hW, -hH, -hD)
        glVertex3f(-hW,  hH, -hD)
        glVertex3f( hW,  hH, -hD)
        glEnd()

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_WIRE): return

        # draw
        hW = 0.5 * self.width
        hH = 0.5 * self.height
        hD = 0.5 * self.depth

        glBegin(GL_LINE_LOOP)
        glVertex3f( hW, -hH, -hD)
        glVertex3f( hW,  hH, -hD)
        glVertex3f( hW,  hH,  hD)
        glVertex3f( hW, -hH,  hD)
        glEnd()
        glBegin(GL_LINE_LOOP)
        glVertex3f(-hW, -hH, -hD)
        glVertex3f(-hW, -hH,  hD)
        glVertex3f(-hW,  hH,  hD)
        glVertex3f(-hW,  hH, -hD)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f( hW, -hH, -hD)
        glVertex3f(-hW, -hH, -hD)
        glVertex3f( hW,  hH, -hD)
        glVertex3f(-hW,  hH, -hD)
        glVertex3f( hW,  hH,  hD)
        glVertex3f(-hW,  hH,  hD)
        glVertex3f( hW, -hH,  hD)
        glVertex3f(-hW, -hH,  hD)
        glEnd()

        # end display-list definition
        self.endDispList(DLF_WIRE)
        return

#----------------------------------------------------------------------
class Ball(GfxNode):
    """
    球クラス
    Ballクラスは，球を表すシーングラフノードクラスです．
    指定された半径(radius)に対し，中心をローカル座標系の原点とする球を
    レンダリングします．
    Ballクラスは8面体を基本形状とし，各三角形を4つの小三角形に分割する操作を
    再帰的に繰り返すことによって球体を表現します．
      radius: 半径
      subdiv: 再分割回数
    """

    """基本頂点"""
    __surface = (
        Vec3(( 0.0, 1.0, 0.0)), Vec3(( 1.0, 0.0, 0.0)), Vec3(( 0.0, 0.0, 1.0)),
        Vec3((-1.0, 0.0, 0.0)), Vec3(( 0.0, 0.0,-1.0)), Vec3(( 0.0,-1.0, 0.0)))
    """基本三角形インデックス"""
    __sindex = ((0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4),
                (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1))

    def __init__(self, name =Node._NONAME, suicide =False,
                 radius=0.5, subdiv=2):
        GfxNode.__init__(self, name, suicide)
        self.radius = radius
        self.subdiv = subdiv
        self.alcData(nV=1)
        self._verts[0][:] = (0, 0, 0)
        self.generateBbox()

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        self._bbox[0][0] = -self.radius
        self._bbox[1][0] =  self.radius
        self._bbox[0][1] = -self.radius
        self._bbox[1][1] =  self.radius
        self._bbox[0][2] = -self.radius
        self._bbox[1][2] =  self.radius

    def drawFace(self, v1, v2, v3, phase):
        """
        三角形描画
        - v1, v2, v3: 頂点座標
        - phase: 球面上の位相(未使用)
        """
        if self._renderMode == RT_NONE :
            return
        elif self._renderMode == RT_WIRE :
            glBegin(GL_LINE_LOOP)
        else :
            glBegin(GL_POLYGON)

        glNormal3f(v1[0], v1[1], v1[2])
        glVertex3f(v1[0]*self.radius, v1[1]*self.radius, v1[2]*self.radius)
        glNormal3f(v2[0], v2[1], v2[2])
        glVertex3f(v2[0]*self.radius, v2[1]*self.radius, v2[2]*self.radius)
        glNormal3f(v3[0], v3[1], v3[2])
        glVertex3f(v3[0]*self.radius, v3[1]*self.radius, v3[2]*self.radius)

        glEnd()
        return

    def subdivFace(self, v1, v2, v3, level, phase):
        """
        三角形再分割
        - v1, v2, v3: 頂点座標
        - level: 再分割レベル
        - phase: 球面上の位相(未使用)
        """
        if level <= 0 :
            self.drawFace(v1, v2, v3, phase)
            return

        v12, v23, v31 = Vec3(), Vec3(), Vec3()
        for i in range(3):
            v12[i] = v1[i] + v2[i]
            v23[i] = v2[i] + v3[i]
            v31[i] = v3[i] + v1[i]
        v12 = v12.unit()
        v23 = v23.unit()
        v31 = v31.unit()

        self.subdivFace(v1,  v12, v31, level -1, phase)
        self.subdivFace(v2,  v23, v12, level -1, phase)
        self.subdivFace(v3,  v31, v23, level -1, phase)
        self.subdivFace(v12, v23, v31, level -1, phase)
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # draw
        for i in range(8):
            self.subdivFace(Ball.__surface[Ball.__sindex[i][0]],
                            Ball.__surface[Ball.__sindex[i][1]],
                            Ball.__surface[Ball.__sindex[i][2]],
                            self.subdiv, i);

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        self.renderSolid()
        return

#----------------------------------------------------------------------
class Cone(GfxNode):
    """
    円錐クラス
    Coneクラスは，円錐を表すシーングラフノードクラスです．
    指定された高さと底面半径(radius)に対し，中心をローカル座標系の原点とする
    円錐をレンダリングします．
    Coneクラスは四角錐を基本形状とし，底面の一辺を2つに分割する操作を再帰的に
    繰り返すことによって円錐を表現します．
      height: 高さ
      radius: 底面半径
      subdiv: 再分割回数
      showBottom: 底面表示フラグ
    """

    """基本頂点"""
    __surface = (
        Vec3(( 0.0, 1.0, 0.0)), Vec3(( 1.0,-1.0, 0.0)), Vec3(( 0.0,-1.0, 1.0)),
        Vec3((-1.0,-1.0, 0.0)), Vec3(( 0.0,-1.0,-1.0)), Vec3(( 0.0,-1.0, 0.0)))
    """基本法線ベクトル"""
    __snormal = (Vec3((0.0, 1.0, 0.0)), Vec3((0.0, -1.0, 0.0)))
    """基本面インデックス"""
    __sindex = ((0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4),
                (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1))
    
    def __init__(self, name =Node._NONAME, suicide =False,
                 radius=0.5, height=1.0, subdiv=2, showBottom=True):
        GfxNode.__init__(self, name, suicide)
        self.radius = radius
        self.height = height
        self.subdiv = subdiv
        self.showBottom = showBottom
        self.alcData(nV=1)
        self._verts[0][:] = (0, 0, 0)
        self.generateBbox()

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        self._bbox[0][0] = -self.radius
        self._bbox[0][1] = -self.height*0.5
        self._bbox[0][2] = -self.radius
        self._bbox[1][0] =  self.radius
        self._bbox[1][1] =  self.height*0.5
        self._bbox[1][2] =  self.radius

    def drawFace(self, v1, v2, v3, phase):
        """
        三角形描画
        - v1, v2, v3: 頂点座標
        - phase: 面上の位相(未使用)
        """
        if self._renderMode == RT_NONE :
            return
        elif self._renderMode == RT_WIRE :
            glBegin(GL_LINE_LOOP)
        else :
            glBegin(GL_POLYGON)

        hH = self.height * 0.5
        if v1[1] > 0.5:
            glNormal3f(Cone.__snormal[0][0],
                       Cone.__snormal[0][1], Cone.__snormal[0][2])
            glVertex3f(v1[0]*self.radius, v1[1]*hH, v1[2]*self.radius)
            glNormal3f(v2[0], 0.0, v2[2])
            glVertex3f(v2[0]*self.radius, v2[1]*hH, v2[2]*self.radius)
            glNormal3f(v3[0], 0.0, v3[2])
            glVertex3f(v3[0]*self.radius, v3[1]*hH, v3[2]*self.radius)
        else :
            glNormal3f(Cone.__snormal[1][0],
                       Cone.__snormal[1][1], Cone.__snormal[1][2])
            glVertex3f(v1[0]*self.radius, v1[1]*hH, v1[2]*self.radius)
            glVertex3f(v2[0]*self.radius, v2[1]*hH, v2[2]*self.radius)
            glVertex3f(v3[0]*self.radius, v3[1]*hH, v3[2]*self.radius)
        glEnd()
        return

    def subdivFace(self, v1, v2, v3, level, phase):
        """
        三角形再分割
        - v1, v2, v3: 頂点座標
        - level: 再分割レベル
        - phase: 面上の位相(未使用)
        """
        if level <= 0 :
            self.drawFace(v1, v2, v3, phase)
            return

        v23 = Vec3()
        v23[0] = v2[0] + v3[0]
        v23[1] = 0.0
        v23[2] = v2[2] + v3[2]
        v23 = v23.unit()
        v23[1] = v2[1]
        self.subdivFace(v1, v2, v23, level -1, phase)
        self.subdivFace(v1, v23, v3, level -1, phase)
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # draw
        for i in range(4):
            self.subdivFace(Cone.__surface[Cone.__sindex[i][0]],
                            Cone.__surface[Cone.__sindex[i][1]],
                            Cone.__surface[Cone.__sindex[i][2]],
                            self.subdiv, i)
        if self.showBottom:
            for i in range(4, 8):
                self.subdivFace(Cone.__surface[Cone.__sindex[i][0]],
                                Cone.__surface[Cone.__sindex[i][1]],
                                Cone.__surface[Cone.__sindex[i][2]],
                                self.subdiv, i)
                
        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        self.renderSolid()
        return

#----------------------------------------------------------------------
class Cylinder(GfxNode):
    """
    円柱クラス
    Cylinderクラスは，円柱を表すシーングラフノードクラスです．
    指定された高さと底面半径(radius)に対し，中心をローカル座標系の原点とする
    円柱をレンダリングします．
    Cylinderクラスは四角柱を基本形状とし，円周方向の一辺を2つに分割する操作を
    再帰的に繰り返すことによって円柱を表現します．
      height: 高さ
      radius: 底面半径
      subdiv: 再分割回数
      showBottom: 底面表示フラグ
      showTop: 上面表示フラグ
    """

    """基本頂点"""
    __surface = (
        Vec3(( 0.0, 1.0, 0.0)), Vec3(( 1.0, 1.0, 0.0)), Vec3(( 0.0, 1.0, 1.0)),
        Vec3((-1.0, 1.0, 0.0)), Vec3(( 0.0, 1.0,-1.0)),
        Vec3(( 1.0,-1.0, 0.0)), Vec3(( 0.0,-1.0, 1.0)), Vec3((-1.0,-1.0, 0.0)),
        Vec3(( 0.0,-1.0,-1.0)), Vec3(( 0.0,-1.0, 0.0)))
    """上底面法線ベクトル"""
    __snormal = (Vec3((0.0, 1.0, 0.0)), Vec3((0.0, -1.0, 0.0)))
    """基本上底面インデックス"""
    __tindex = ((0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4),
                (9, 5, 6), (9, 6, 7), (9, 7, 8), (9, 8, 5))
    """基本側面インデックス"""
    __qindex = ((1, 2, 6, 5), (2, 3, 7, 6), (3, 4, 8, 7), (4, 1, 5, 8))

    def __init__(self, name =Node._NONAME, suicide =False,
                 radius=0.5, height=1.0, subdiv=2,
                 showBottom=True, showTop=True):
        GfxNode.__init__(self, name, suicide)
        self.radius = radius
        self.height = height
        self.subdiv = subdiv
        self.showBottom = showBottom
        self.showTop = showTop
        self.alcData(nV=1)
        self._verts[0][:] = (0, 0, 0)
        self.generateBbox()

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        self._bbox[0][0] = -self.radius
        self._bbox[0][1] = -self.height*0.5
        self._bbox[0][2] = -self.radius
        self._bbox[1][0] =  self.radius
        self._bbox[1][1] =  self.height*0.5
        self._bbox[1][2] =  self.radius

    def drawTri(self, v1, v2, v3):
        """
        上底面三角形描画
        - v1, v2, v3: 頂点座標
        """
        if self._renderMode == RT_NONE :
            return
        elif self._renderMode == RT_WIRE :
            glBegin(GL_LINE_LOOP)
        else :
            glBegin(GL_POLYGON)

        if v1[1] > 0.0:
            glNormal3f(Cylinder.__snormal[0][0],
                       Cylinder.__snormal[0][1], Cylinder.__snormal[0][2])
        else:
            glNormal3f(Cylinder.__snormal[1][0],
                       Cylinder.__snormal[1][1], Cylinder.__snormal[1][2])
        hH = self.height * 0.5
        glVertex3f(v1[0]*self.radius, v1[1]*hH, v1[2]*self.radius)
        glVertex3f(v2[0]*self.radius, v2[1]*hH, v2[2]*self.radius)
        glVertex3f(v3[0]*self.radius, v3[1]*hH, v3[2]*self.radius)
        glEnd()
        return

    def drawQuad(self, v1, v2, v3, v4, phase):
        """
        側面四角形描画
        - v1, v2, v3, v4: 頂点座標
        - phase: 側面上の位相(未使用)
        """
        if self._renderMode == RT_NONE :
            return
        elif self._renderMode == RT_WIRE :
            glBegin(GL_LINE_LOOP)
        else :
            glBegin(GL_POLYGON)

        hH = self.height * 0.5
        glNormal3f(v1[0], 0.0, v1[2])
        glVertex3f(v1[0]*self.radius, v1[1]*hH, v1[2]*self.radius)
        glNormal3f(v2[0], 0.0, v2[2])
        glVertex3f(v2[0]*self.radius, v2[1]*hH, v2[2]*self.radius)
        glNormal3f(v3[0], 0.0, v3[2])
        glVertex3f(v3[0]*self.radius, v3[1]*hH, v3[2]*self.radius)
        glNormal3f(v4[0], 0.0, v4[2])
        glVertex3f(v4[0]*self.radius, v4[1]*hH, v4[2]*self.radius)
        glEnd()
        return

    def subdivTri(self, v1, v2, v3, level):
        """
        上底面三角形再分割
        - v1, v2, v3: 頂点座標
        - level: 再分割レベル
        """
        if level <= 0 :
            self.drawTri(v1, v2, v3)
            return

        v23 = Vec3()
        v23[0] = v2[0] + v3[0]
        v23[1] = 0.0
        v23[2] = v2[2] + v3[2]
        v23 = v23.unit()
        v23[1] = v2[1]
        self.subdivTri(v1, v2, v23, level -1)
        self.subdivTri(v1, v23, v3, level -1)
        return

    def subdivQuad(self, v1, v2, v3, v4, level, phase):
        """
        側面四角形再分割
        - v1, v2, v3, v4: 頂点座標
        - level: 再分割レベル
        - phase: 側面上の位相(未使用)
        """
        if level <= 0 :
            self.drawQuad(v1, v2, v3, v4, phase)
            return

        v12, v34 = Vec3(), Vec3()
        v12[0] = v1[0] + v2[0]
        v12[1] = 0.0
        v12[2] = v1[2] + v2[2]
        v12 = v12.unit()
        v12[1] = v1[1]
        v34[0] = v3[0] + v4[0]
        v34[1] = 0.0
        v34[2] = v3[2] + v4[2]
        v34 = v34.unit()
        v34[1] = v3[1]
        self.subdivQuad(v1, v12, v34, v4, level -1, phase)
        self.subdivQuad(v12, v2, v3, v34, level -1, phase)
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # draw
        if self.showTop:
            for i in range(4):
                self.subdivTri(Cylinder.__surface[Cylinder.__tindex[i][0]],
                               Cylinder.__surface[Cylinder.__tindex[i][1]],
                               Cylinder.__surface[Cylinder.__tindex[i][2]],
                               self.subdiv)
        if self.showBottom:
            for i in range(4, 8):
                self.subdivTri(Cylinder.__surface[Cylinder.__tindex[i][0]],
                               Cylinder.__surface[Cylinder.__tindex[i][1]],
                               Cylinder.__surface[Cylinder.__tindex[i][2]],
                               self.subdiv)
        for i in range(4):
            self.subdivQuad(Cylinder.__surface[Cylinder.__qindex[i][0]],
                            Cylinder.__surface[Cylinder.__qindex[i][1]],
                            Cylinder.__surface[Cylinder.__qindex[i][2]],
                            Cylinder.__surface[Cylinder.__qindex[i][3]],
                            self.subdiv, i)

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        self.renderSolid()
        return
