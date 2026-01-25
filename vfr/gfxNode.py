#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import numpy as N
import ctypes as C
from OpenGL.GL import *
from .node import *
from .obj import *
from .utilMath import *


#----------------------------------------------------------------------
"""レンダリングモードタイプ"""
(RT_NONE, RT_SMOOTH, RT_FLAT, RT_NOLIGHT,
 RT_WIRE, RT_POINT, RT_NOTEXTURE) = (0,) + tuple([(1<<x) for x in range(6)])
"""セレクションテスト対象タイプ"""
(PT_NONE, PT_OBJECT, PT_BBOX) = (0,) + tuple([(1<<x) for x in range(2)])
"""表面属性タイプ"""
(AT_WHOLE, AT_PER_VERTEX, AT_PER_FACE) = range(3)
"""フィードバックテストモード"""
(FB_VERTEX, FB_FACE, FB_EDGE) = range(3)
"""線種タイプ"""
(ST_SOLID, ST_DOT, ST_DASH, ST_DDASH1, ST_DDASH2) = range(5)
"""光源タイプ"""
(LT_DIRECTIONAL, LT_POINT, LT_SPOT) = range(3)
"""表示面タイプ"""
(PF_FRONT, PF_BACK, PF_BOTH) = (GL_FRONT, GL_BACK, GL_FRONT_AND_BACK)
"""アライメントタイプ"""
(AL_LEFT, AL_RIGHT, AL_CENTER) = range(3)
"""投影タイプ"""
(PR_PERSPECTIVE, PR_ORTHOGONAL) = range(2)
"""ポイントシンボルタイプ"""
(SYM_NORMAL, SYM_PLUS, SYM_CROSS,
 SYM_CIRCLE, SYM_CIRCFILL, SYM_SQUARE, SYM_SQUAFILL,
 SYM_TRIANGLE, SYM_TRIAFILL) = range(9)
"""ディスプレイリスト種別"""
(DLF_POINT, DLF_WIRE, DLF_SOLID) = tuple([(1<<x) for x in range(3)])


#----------------------------------------------------------------------
class Point2(object):
    """
    2Dポイントクラス
    Point2クラスは，(x, y)で表現される２次元の点(座標)を表現するクラスです．
    """
    def __init__(self, x =0, y =0):
        self.x = x
        self.y = y
    def __eq__(self, a):
        if 'x' in dir(a) and 'y' in dir(a):
            return (self.x == a.x and self.y == a.y)
        return False
    def __ne__(self, a):
        return not self.__eq__(a)
    def __add__(self, a):
        b = Point2(self.x, self.y)
        try:
            b.x = b.x + a.x
            b.y = b.y + a.y
        except: pass
        return b
    __iadd__ = __add__
    def __neg__(self):
        return Point2(-self.x, -self.y)
    def __sub__(self, a):
        return self.__add__(-a)
    __isub__ = __sub__
    def __str__(self):
        return str((self.x, self.y,))
    def __repr__(self):
        return 'Point2'+self.__str__()
    def __getitem__(self, index):
        if index == 0: return self.x
        elif index == 1: return self.y
        else: raise IndexError
    def __setitem__(self, index, val):
        if index == 0: self.x = val
        elif index == 1: self.y = val
        else: raise IndexError


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


class GfxNode(Node, Obj):
    """
    シーングラフ・ノードクラス
    GfxNodeクラスは、OpenGLによるレンダリング機能をもつシーングラフノードの
    基底クラスです.
      _matrix: 幾何変換行列．ローカル座標系の幾何変換を表します．
          utilMath.Mat4です．
      _transparent: 不透明モード
      _normalMode: 法線ベクトルタイプ(AT_WHOLE,AT_PER_VERTEX,AT_PER_FACE)
      _colorMode: 色タイプ(AT_WHOLE,AT_PER_VERTEX,AT_PER_FACE)
      _feedbackMode: フィードバックテストタイプ(FB_VERTEX,FB_FACE,FB_EDGE)
      _useLocalMaterial: 自分自身のマテリアル情報を有効にするか
      _renderMode: レンダリングモード(RT_NONE,RT_SMOOTH,RT_FLAT,RT_NOLIGHT,
           RT_WIRE,RT_POINT,RT_NOTEXTUREの合成)
      _pickable: セレクション対象フラグ
      _faceMode: ポリゴンフェースモード(PF_FRONT,PF_BACK,PF_BOTH)
      _bbox: バウンディングボックス(頂点座標の存在範囲).
           (utilMath.Vec3, utilMath.Vec3)です.
      _specular, _ambient, _shininess, _emission: 反射係数
      _lineStipple: 線種(ST_SOLID,ST_DOT,ST_DASH,ST_DDASH1,ST_DDASH2)
      _lineWidth: 線幅
      _auxLineColor: ライン代替色
      _useAuxLineColor: ライン代替色モード
      _pointSymbol: ポイントタイプ(SYM_NORMAL,SYM_PLUS,SYM_CROSS,SYM_CIRCLE,
           SYM_CIRCFILL,SYM_SQUARE,SYM_SQUAFILL,SYM_TRIANGLE,SYM_TRIAFILL)
      _pointSize: ポイントサイズ
      _auxPointColor: ポイント代替色
      _useAuxPointColor: ポイント代替色モード
      _dlPoint, _dlWire, _dlSolid: OpenGLディスプレイリスト
      _dlUpdated: ディスプレイリスト更新フラグ
      _dlNodeType: ディスプレイリスト使用ノードフラグ
    以下のメンバー変数は，obj.Objクラスで実装されています．
      _verts: 頂点座標配列．ctypes.POINTER(ctypes.c_float*3)です．
      _normals: 法線ベクトル配列．ctypes.POINTER(ctypes.c_float*3)です．
      _colors: 色(RGBA)配列．ctypes.POINTER(ctypes.c_float*4)です．
      _indices: インデックス配列．ctypes.POINTER(ctypes.c_int)です．
      nVerts: 頂点データ数
      nNormals: 法線ベクトルデータ数
      nIndices: インデックスデータ数
      nColors: 色データ数
    """

    """フィードバックテスト用バッファサイズの基準数"""
    FEEDBACK_SIZE_FACTOR = 8

    """ラインのパターン"""
    __stipplePattern = {ST_SOLID:0xFFFF, ST_DOT:0x3333, ST_DASH:0x00FF,
                        ST_DDASH1:0x88FF, ST_DDASH2:0x111F}

    """ディスプレイリスト使用モード"""
    __useDispList = True
    
    def __init__(self, **args):
        """
        args: localMaterial =True
        """
        Node.__init__(self, **args)
        Obj.__init__(self)

        self.alcData(nC=1)
        self._colors[0][:] = (0.9, 0.9, 0.9, 1.0)

        self._matrix = Mat4()
        self._transparent = False
        self._normalMode = AT_WHOLE
        self._colorMode = AT_WHOLE
        self._feedbackMode = FB_VERTEX

        self._useLocalMaterial = True if not 'localMaterial' in args \
            else args['localMaterial']
        self._specular = [0.0, 0.0, 0.0, 1.0]
        self._ambient = [0.2, 0.2, 0.2, 1.0]
        self._shininess = [5.0]
        self._emission = [0.0, 0.0, 0.0, 1.0]
        self._lineStipple = ST_SOLID
        self._lineWidth = 1.0
        self._pointSize = 1.0
        self._pointSymbol = SYM_NORMAL
        self._renderMode = RT_SMOOTH
        self._faceMode = PF_BOTH

        self._auxLineColor = [1.0, 1.0, 1.0, 1.0]
        self._useAuxLineColor = False
        self._auxPointColor = [1.0, 1.0, 1.0, 1.0]
        self._useAuxPointColor = False

        self._shader = None
        self._texture = None

        self._showBbox = False
        self._pickable = PT_NONE
        self._bboxColor = [0.6, 0.6, 0.6, 1.0]
        self._bboxWidth = 2.0

        self._dlPoint = 0
        self._dlWire = 0
        self._dlSolid = 0
        self._dlUpdated = 0
        self._dlNodeType = True
        return

    def __del__(self):
        Node.__del__(self)
        Obj.__del__(self)
        return

    def destroy(self):
        """
        無効化
        アロケートしているデータを解放し，ディスプレイリストを無効化し，
        基底クラスのdestroy()を呼び出します．
        """
        Node.destroy(self)
        self.clearDispList()
        self.alcData(nV=0, nN=0, nI=0, nC=1)
        self._colors[0][0:4] = (0.9, 0.9, 0.9, 1.0)

    #-------- matrix interface --------
    def identity(self):
        """
        幾何変換の初期化
        """
        self._matrix.Identity()
        self.notice(False)

    def rotx(self, r):
        """
        X軸周りの回転
        - r: 回転角度(rad)
        """
        self._matrix.RotX(r)
        self.notice(False)

    def roty(self, r):
        """
        Y軸周りの回転
        - r: 回転角度(rad)
        """
        self._matrix.RotY(r)
        self.notice(False)

    def rotz(self, r):
        """
        Z軸周りの回転
        - r: 回転角度(rad)
        """
        self._matrix.RotZ(r)
        self.notice(False)

    def rotation(self, a, v):
        """
        任意軸周りの回転
        - a: 回転角度(rad)
        - v: 回転軸方向ベクトル
        """
        self._matrix.Rotation(a, v)
        self.notice(False)

    def trans(self, v):
        """
        平行移動
        - v: 移動量ベクトル
        """
        self._matrix.Translate(v)
        self.notice(False)

    def scale(self, v):
        """
        スケーリング
        - v: スケーリングファクターベクトル(各軸方向)
        """
        self._matrix.Scale(v)
        self.notice(False)

    def mult(self, m):
        """
        幾何変換行列の適用
        現在の幾何変換行列に，指定された幾何変換行列を掛けます．
        - m: 幾何変換行列
        """
        self._matrix = self._matrix * m
        self.notice(False)

    def setMatrix(self, m):
        """
        幾何変換行列の設定
        現在の幾何変換行列を，指定された幾何変換行列で置換えます．
        - m: 幾何変換行列
        """
        self._matrix[0:] = m[0:]
        self.notice(False)

    def getMatrix(self):
        """
        幾何変換行列を返す
        """
        return self._matrix

    def setHpr(self, h =0.0, p =0.0, r =0.0):
        """
        姿勢設定
        HPR(Head, Pitch, Roll)による姿勢設定を行います．
        - h: Yaw値(Y軸周りの回転量, rad)
        - p: Pitch値(X軸周りの回転量, rad)
        - r: Roll値(Z軸周りの回転量, rad)
        """
        # set M to R * P * H
        tv = self._matrix.m_v[12:15]
        self._matrix.Identity()
        self._matrix.RotY(h)
        self._matrix.RotX(p)
        self._matrix.RotZ(r)
        self._matrix.m_v[12:15] = tv[0:3]
        self._matrix.m_v[15] = 1.0
        self.notice(False)
        return

    def accumMatrix(self, tid, M):
        """
        幾何変換行列の累積演算
        指定されたIDを持つノードまでの幾何変換行列の累積演算を行い、
        Mに適用します.
        自分自身のID番号と指定されたID番号が異なる場合はFalseを返します.
        - tid: ターゲットノードのID
        - M: 幾何変換行列
        """
        if not tid == self._id:
            return False
        M1 = M * self._matrix
        M.m_v[0:] = M1.m_v[0:]
        return True

    def applyMatrix(self):
        """
        幾何変換適用
        幾何変換をOpenGLに適用します．
        """
        glPushMatrix()
        glMultMatrixf(self._matrix.m_v.tolist())
        return

    def unApplyMatrix(self):
        """
        幾何変換無効化
        OpenGLに適用した幾何変換を無効化します．
        """
        glPopMatrix()
        return

    #-------- alpha interface --------
    def setTransparency(self, tm):
        """
        半透明モード設定
        - tm: 半透明モード
        """
        if self._transparent == tm: return
        self._transparent = tm
        self.notice(False)
        return

    def setAlpha(self, alp, tm =True):
        """
        半透明パラメータ設定
        - alp: 不透明度
        - tm: 半透明モード
        """
        for i in range(self.nColors):
            self._colors[i][3] = alp
        self._transparent = tm
        self.notice()
        return

    def isTransparency(self):
        """
        半透明モードかどうかを返す
        """
        return self._transparent

    #-------- memory interface --------
    def getNumVerts(self):
        """頂点数を返す"""
        return self.nVerts

    def getNumIndices(self):
        """インデックスデータ数を返す"""
        return self.nIndices

    def getNumNormals(self):
        """法線ベクトル数を返す"""
        return self.nNormals

    def getNumColors(self):
        """色データ数を返す"""
        return self.nColors

    def setVert(self, idx, value, update=False):
        """指定されたインデックスの頂点座標を設定する"""
        if idx < 0 or idx > self.nVerts: return False
        try:
            self._verts[idx][:] = value[:]
        except:
            return False
        if update:
            self.updateBbox(value)
            self.notice()
        return True

    def setNormal(self, idx, value, update=False):
        """指定されたインデックスの法線ベクトルを設定する"""
        if idx < 0 or idx > self.nNormals: return False
        try:
            self._normals[idx][:] = value[:]
        except:
            return False
        if update: self.notice()
        return True

    def setIndice(self, idx, value, update=False):
        """指定されたインデックスのインデックスデータを設定する"""
        if idx < 0 or idx > self.nIndices: return False
        try:
            self._indices[idx] = value
        except:
            return False
        if update: self.notice()
        return True

    def setColor(self, idx, value, update=False):
        """指定されたインデックスの色データを設定する"""
        if idx < 0 or idx > self.nColors: return False
        try:
            self._colors[idx][:] = value[:]
        except:
            try:
                self._colors[idx][0:3] = value[0:3]
            except:
                return False
        if update: self.notice()
        return True

    def generateNormals(self):
        """
        法線ベクトル再計算
        派生クラスで実装されます．
        """
        return False;

    #-------- display list interface --------
    def beginDispList(self, targ):
        """
        ディスプレイリスト定義開始
        OpenGLディスプレイリストの定義を開始します．
        指定ターゲットのディスプレイリストが有効であればFalseを返し，
        無効(ディスプレイリストの再作成が必要)の場合はTrueを返します．
        - targ: ターゲット
                DLF_POINT: ポイントレンダリング用ディスプレイリスト
                DLF_WIRE: ワイヤーフレームレンダリング用ディスプレイリスト
                DLF_SOLID: ソリッドレンダリング用ディスプレイリスト
        """
        if not self._dlNodeType: return False
        if not GfxNode.__useDispList: return False
        if self._dlUpdated & targ:
            if targ == DLF_POINT: glCallList(self._dlPoint)
            elif targ == DLF_WIRE: glCallList(self._dlWire)
            elif targ == DLF_SOLID: glCallList(self._dlSolid)
            else: return False
            return True
        if targ == DLF_POINT:
            if self._dlPoint < 1:
                self._dlPoint = glGenLists(1)
            glNewList(self._dlPoint, GL_COMPILE_AND_EXECUTE)
        elif targ == DLF_WIRE:
            if self._dlWire < 1:
                self._dlWire = glGenLists(1)
            glNewList(self._dlWire, GL_COMPILE_AND_EXECUTE)
        elif targ == DLF_SOLID:
            if self._dlSolid < 1:
                self._dlSolid = glGenLists(1)
            glNewList(self._dlSolid, GL_COMPILE_AND_EXECUTE)
        return False

    def endDispList(self, targ):
        """
        ディスプレイリスト定義終了
        """
        if not self._dlNodeType: return
        if not GfxNode.__useDispList: return
        if targ == DLF_POINT and self._dlPoint > 0: pass
        elif targ == DLF_WIRE and self._dlWire > 0: pass
        elif targ == DLF_SOLID and self._dlSolid > 0: pass
        else: return
        glEndList()
        self._dlUpdated = self._dlUpdated | targ
        return

    def invalidateDispList(self):
        """
        OpenGLディスプレイリストの無効化
        """
        if self._dlNodeType: self._dlUpdated = 0
        return

    def clearDispList(self):
        """
        OpenGLディスプレイリストの破棄
        """
        if not self._dlNodeType: return
        if self._dlPoint > 0:
            glDeleteLists(self._dlPoint, 1)
            self._dlPoint = 0
        if self._dlWire > 0:
            glDeleteLists(self._dlWire, 1)
            self._dlWire = 0
        if self._dlSolid > 0:
            glDeleteLists(self._dlSolid, 1)
            self._dlSolid = 0
        self._dlUpdated = 0
        return

    #-------- material interface --------
    def applyMaterial(self):
        """
        マテリアル属性適用
        設定されているマテリアル属性をOpenGLに適用します．
        """
        if not self._useLocalMaterial: return
        
        glMaterialfv(self._faceMode, GL_AMBIENT, self._ambient)
        glMaterialfv(self._faceMode, GL_SPECULAR, self._specular)
        glMaterialfv(self._faceMode, GL_SHININESS, self._shininess)
        glMaterialfv(self._faceMode, GL_EMISSION, self._emission)
        glColorMaterial(self._faceMode, GL_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        glPointSize(self._pointSize)
        glLineWidth(self._lineWidth)
        if not self._lineStipple == ST_SOLID :
            glEnable(GL_LINE_STIPPLE);
            glLineStipple(1, GfxNode.__stipplePattern[self._lineStipple])

        if not self._faceMode == GL_FRONT_AND_BACK:
            glCullFace(self._faceMode)

        if not self._renderMode == RT_NONE:
            if not self._faceMode == GL_FRONT_AND_BACK:
                glEnable(GL_CULL_FACE)
            else:
                glDisable(GL_CULL_FACE)
        return

    def unApplyMaterial(self):
        """
        マテリアル属性無効化
        OpenGLに適用したマテリアル属性を無効化します．
        """
        if not self._useLocalMaterial: return

        if not self._lineStipple == ST_SOLID:
            glLineStipple(1, GfxNode.__stipplePattern[ST_SOLID])
            glDisable(GL_LINE_STIPPLE)
        if not self._renderMode == RT_NONE:
            if not self._faceMode == GL_FRONT_AND_BACK:
                glDisable(GL_CULL_FACE)
        return

    #-------- render interface --------
    def render_(self, transpMode):
        """
        レンダリング(半透明モード指定)
        半透明モードを指定してrender_()を呼び出します.
        - transpMode: 半透明モード
        """
        if transpMode :
            if self._transparent :
                self.render()
        else :
            if not self._transparent :
                self.render()
        return

    def render(self):
        """
        レンダリング
        OpenGLによるレンダリングを行います.
        """
        # push name for selection
        if self._pickable & PT_OBJECT :
            glPushName(self._id)

        # transformation matrix
        self.applyMatrix()

        # apply material
        self.applyMaterial()

        # apply texture
        if self._texture != None:
            self._texture.enable()
        
        # apply shader
        if self._shader != None:
            glUseProgram(self._shader.program_id)
        
        # rendering
        if self._renderMode & (RT_SMOOTH | RT_NOLIGHT | RT_FLAT) :
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            if self._renderMode & RT_NOLIGHT :
                glDisable(GL_LIGHTING)
            if self._colorMode == AT_WHOLE :
                glColor4fv(self._colors[0])
            self.renderSolid()

        if self._renderMode & RT_WIRE :
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDisable(GL_LIGHTING)
            if self._useAuxLineColor:
                glColor4fv(self._auxLineColor)
            elif self._colorMode == AT_WHOLE :
                glColor4fv(self._colors[0])
            self.renderWire()
            glEnable(GL_LIGHTING)

        if self._renderMode & RT_POINT :
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
            glDisable(GL_LIGHTING)
            if self._useAuxPointColor:
                glColor4fv(self._auxPointColor)
            elif self._colorMode == AT_WHOLE :
                glColor4fv(self._colors[0])
            self.renderPoint()
            glEnable(GL_LIGHTING)

        # unapply shader
        if self._shader != None:
            glUseProgram(0)

        # un-apply texture
        if self._texture != None:
            self._texture.disable()

        # un-apply material
        self.unApplyMaterial()

        # draw bbox
        if self._showBbox:
            if self._pickable & PT_OBJECT:
                if not self._pickable & PT_BBOX:
                    glLoadName(0)
            self.drawBbox()

        # pop name for selection
        if self._pickable & PT_OBJECT:
            glPopName()

        # pop transformation matrix
        self.unApplyMatrix()
        return

    def drawBbox(self):
        """
        バウンディングボックス描画
        バウンディングボックスをOpenGLでワイヤーフレーム表示します
        """
        glDisable(GL_LIGHTING)
        glLineWidth(self._bboxWidth)
        glColor4fv(self._bboxColor)

        glBegin(GL_LINE_LOOP)
        glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[0][2])
        glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[0][2])
        glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[1][2])
        glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[1][2])
        glEnd()

        glBegin(GL_LINE_LOOP)
        glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[0][2])
        glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[1][2])
        glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[1][2])
        glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[0][2])
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[0][2])
        glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[0][2])

        glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[0][2])
        glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[0][2])

        glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[1][2])
        glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[1][2])

        glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[1][2])
        glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[1][2])
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        派生クラスで実装されます．
        """
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        派生クラスで実装されます．
        """
        return

    def renderPoint(self):
        """
        ポイントレンダリング
        ポイントモードでOpenGLによるレンダリングを行います．
        """
        if self.nVerts < 1: return
        
        # display-list check
        if self.beginDispList(DLF_POINT): return

        # draw points via gfxNode_DrawPoints
        nv = self.nVerts
        vtx = self._verts
        if self._colorMode == AT_WHOLE or self._useAuxPointColor:
            nc = 0
            col = None
        else:
            nc = self.nColors
            col = self._colors
        ret = vfr_impl.gfxNode_DrawPoints(nv, vtx,  nc, col,
                                          self._pointSymbol, 0)
        if ret == 0: pass

        # end display-list definition
        self.endDispList(DLF_POINT)
        return

    def renderBbox(self):
        """
        バウンディングボックスレンダリング
        バウンディングボックスのOpenGLによるレンダリングを行います．
        """
        self.applyMatrix();
        glPushName(self._id)
        if self._renderMode == RT_NONE:
            pass
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[1][2])
            glEnd()
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[0][2])
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[1][2])
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[0][2])
            glEnd()
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[0][2])
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[0][2])
            glEnd()
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[1][2])
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[1][2])
            glEnd()
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[1][2])
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[1][2])
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[1][2])
            glEnd()
            glBegin(GL_POLYGON)
            glVertex3f(self._bbox[0][0], self._bbox[0][1], self._bbox[0][2])
            glVertex3f(self._bbox[0][0], self._bbox[1][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[1][1], self._bbox[0][2])
            glVertex3f(self._bbox[1][0], self._bbox[0][1], self._bbox[0][2])
            glEnd()
        glPopName()
        self.unApplyMatrix()
        return

    #-------- feedback interface --------
    def renderFeedBack(self, tgt):
        """
        フィードバックテスト用レンダリング
        フィードバックテストのためのレンダリングを行います.
        指定されたターゲットIDが自分自身のID番号と異なる場合は何もしません．
        - tgt: フィードバックターゲットノードのID
        """
        if not self._id == tgt:
            return

        # transformation matrix
        self.applyMatrix()

        # call gfxNode_DrawPoints
        if self.nVerts > 0:
            ret = vfr_impl.gfxNode_DrawPoints(self.nVerts, self._verts,
                                              0, None,  0, 1)
            if ret == 0: pass

        # un-apply matrix
        self.unApplyMatrix()
        return

    def getFeedbackSize(self):
        """
        フィードバックサイズファクターを返す
        フィードバックテスト結果格納に必要なサイズを算出するための基準値を
        返します．
        """
        fbs = 0
        try:
            if self._feedbackMode == FB_FACE or self._feedbackMode == FB_EDGE:
                fbs = (self.nIndices + self.nVerts) * \
                    GfxNode.FEEDBACK_SIZE_FACTOR
            else:
                fbs = self.nVerts * GfxNode.FEEDBACK_SIZE_FACTOR
        except:
            pass
        return fbs

    #-------- bbox interface --------
    def setBbox(self, min, max):
        """
        バウンディングボックス値を設定する．
        """
        self._bbox[0][:] = min[:]
        self._bbox[1][:] = max[:]
        self.checkBbox()
        return
        
    def getBbox(self):
        """
        バウンディングボックス値を返す．
        """
        return self._bbox
    
    def getMatrixBbox(self, bbox):
        """
        幾何変換を適用したバウンディングボックス値を返す．
        """
        local = [Vec3() for x in range(8)]
        out = Vec3()
        local[0].m_v[0] = self._bbox[1][0]
        local[0].m_v[1] = self._bbox[0][1]
        local[0].m_v[2] = self._bbox[0][2]
        local[1].m_v[0] = self._bbox[1][0]
        local[1].m_v[1] = self._bbox[1][1]
        local[1].m_v[2] = self._bbox[0][2]
        local[2].m_v[0] = self._bbox[1][0]
        local[2].m_v[1] = self._bbox[1][1]
        local[2].m_v[2] = self._bbox[1][2]
        local[3].m_v[0] = self._bbox[1][0]
        local[3].m_v[1] = self._bbox[0][1]
        local[3].m_v[2] = self._bbox[1][2]
        local[4].m_v[0] = self._bbox[0][0]
        local[4].m_v[1] = self._bbox[0][1]
        local[4].m_v[2] = self._bbox[0][2]
        local[5].m_v[0] = self._bbox[0][0]
        local[5].m_v[1] = self._bbox[0][1]
        local[5].m_v[2] = self._bbox[1][2]
        local[6].m_v[0] = self._bbox[0][0]
        local[6].m_v[1] = self._bbox[1][1]
        local[6].m_v[2] = self._bbox[1][2]
        local[7].m_v[0] = self._bbox[0][0]
        local[7].m_v[1] = self._bbox[1][1]
        local[7].m_v[2] = self._bbox[0][2]
        out = self._matrix * local[0]
        box = [Vec3(out), Vec3(out)]
        for i in range(1, 8):
            out = self._matrix * local[i]
            if box[0].m_v[0] > out.m_v[0] : box[0].m_v[0] = out.m_v[0]
            if box[1].m_v[0] < out.m_v[0] : box[1].m_v[0] = out.m_v[0]
            if box[0].m_v[1] > out.m_v[1] : box[0].m_v[1] = out.m_v[1]
            if box[1].m_v[1] < out.m_v[1] : box[1].m_v[1] = out.m_v[1]
            if box[0].m_v[2] > out.m_v[2] : box[0].m_v[2] = out.m_v[2]
            if box[1].m_v[2] < out.m_v[2] : box[1].m_v[2] = out.m_v[2]
        bbox[0].m_v[0:] = box[0].m_v[0:]
        bbox[1].m_v[0:] = box[1].m_v[0:]
        return

    def setBboxShowMode(self, bsm):
        """
        バウンディングボックス表示モードの設定
        - bsm: バウンディングボックス表示モード
        """
        if self._showBbox == bsm: return
        self._showBbox = bsm
        self.notice(False)
        return
    
    def getBboxShowMode(self):
        """
        バウンディングボックス表示モードを返す
        """
        return self._showBbox

    def setBboxColor(self, bbc):
        """
        バウンディングボックスカラーの設定
        - bbc: バウンディングボックスの色(RGBA:0.0〜1.0)
        """
        self._bboxColor[0:] = bbc[0:]
        if self._showBbox:
            self.notice(False)
        return
    
    def getBboxColor(self):
        """
        バウンディングボックスカラーを返す
        """
        return self._bboxColor

    def setBboxWidth(self, bw):
        """
        バウンディングボックス線幅の設定
        - bw: バウンディングボックスの線幅(ピクセル:0.0〜)
        """
        if bw < 0.0: return
        self._bboxWidth = bw
        if self._showBbox:
            self.notice(False)
        return
    
    def getBboxWidth(self):
        """
        バウンディングボックス線幅を返す
        """
        return _bboxWidth

    def updateBbox(self, vtx):
        """
        頂点追加の際のバウンディングボックス更新
        """
        for i in range[3]:
            if self._bbox[0][i] > vtx[i]: self._bbox[0][i] = vtx[i]
            elif self._bbox[1][i] < vtx[i]: self._bbox[1][i] = vtx[i]
        return

    #-------- attribute interface --------
    def setRenderMode(self, rm):
        """
        レンダリングモードの設定
        - rm: レンダリングモード.以下のコンビネーションで指定します．
              RT_NONE: レンダリングしない
              RT_SMOOTH: ポリゴン表示(スムースシェーディング)
              RT_FLAT: ポリゴン表示(フラットシェーディング)
              RT_NOLIGHT: ポリゴン表示(シェーディングなし)
              RT_WIRE: ワイヤーフレーム表示
              RT_POINT: ポイント表示
              RT_NOTEXTURE: テクスチャマッピング無効(未使用)
        """
        if self._renderMode == rm: return
        self._renderMode = rm
        self.notice()

    def getRenderMode(self):
        """
        レンダリングモードを返す
        """
        return self._renderMode

    def setFaceMode(self, fm):
        """
        ポリゴンフェースモードの設定
        - fm: ポリゴンフェースモード
              PF_FRONT: フロントフェースのみ表示
              PF_BACK: バックフェースのみ表示
              PF_BOTH: 両方の面を表示
        """
        if self._faceMode == fm: return
        self._faceMode = fm
        self.notice()

    def getFaceMode(self):
        """
        ポリゴンフェースモードを返す
        """
        return self._faceMode
    
    def setPickMode(self, pm):
        """
        ピックモードの設定
        ピックモード(セレクションテストの対象)を設定します．
        - pm: ピックモード.以下のコンビネーションで指定します．
              PT_NONE: セレクションテストの対象としない
              PT_OBJECT: 形状データをセレクションテストの対象とする
              PT_BBOX: バウンディングボックスをセレクションテストの対象とする
        """
        self._pickable = pm
        return
    
    def getPickMode(self):
        """
        ピックモードを返す
        """
        return self._pickable

    def setNormalMode(self, nm):
        """
        法線ベクトル種別の設定
        - nm: 法線ベクトル種別
              AT_WHOLE: ノードのモデル全体に対して1つ
              AT_PER_VERTEX: 頂点毎に設定
              AT_PER_FACE: 面毎に設定
        """
        if self._normalMode == nm: return
        if nm in (AT_WHOLE, AT_PER_VERTEX, AT_PER_FACE):
            self._normalMode = nm
            self.notice()
        return
    
    def getNormalMode(self):
        """
        法線ベクトル種別を返す
        """
        return self._normalMode

    def setColorMode(self, cm):
        """
        色データ種別の設定
        - cm: 色データ種別
              AT_WHOLE: ノードのモデル全体に対して1つ(単色)
              AT_PER_VERTEX: 頂点毎に設定
              AT_PER_FACE: 面毎に設定
        """
        if self._colorMode == cm: return
        if cm in (AT_WHOLE, AT_PER_VERTEX, AT_PER_FACE):
            self._colorMode = cm
            self.notice()
        return
    
    def getColorMode(self):
        """
        色データ種別を返す
        """
        return self._colorMode

    def setAuxLineColor(self, mode, color =None):
        """
        ライン代替色モードの設定
        ワイヤーフレーム表示の色を、_colorsと別の色で行うかを設定します．
        - mode: ライン代替色モード
        - color: ライン代替色(RGBA: 0.0〜1.0)
        """
        needUpd = False
        if self._useAuxLineColor != mode:
            self._useAuxLineColor = mode
            needUpd = True
        if color:
            self._auxLineColor[0:4] = color[0:4]
            needUpd = True
        if needUpd:
            self.notice()
        return
    
    def getAuxLineColorMode(self):
        """
        ライン代替色モードを返す
        """
        return self._useAuxLineColor

    def getAuxLineColor(self):
        """
        ライン代替色を返す
        """
        return self._auxLineColor

    def setAuxPointColor(self, mode, color =None):
        """
        ポイント代替色モードの設定
        ポイント表示の色を、_colorsと別の色で行うかを設定します．
        - mode: ポイント代替色モード
        - color: ポイント代替色(RGBA: 0.0〜1.0)
        """
        needUpd = False
        if self._useAuxPointColor != mode:
            self._useAuxPointColor = mode
            needUpd = True
        if color:
            self._auxPointColor[0:4] = color[0:4]
            needUpd = True
        if needUpd:
            self.notice()
        return
    
    def getAuxPointColorMode(self):
        """
        ポイント代替色モードを返す
        """
        return self._useAuxPointColor

    def getAuxPointColor(self):
        """
        ポイント代替色を返す
        """
        return self._auxPointColor

    def setFeedbackMode(self, fm):
        """
        フィードバックテストモードの設定
        - fm: フィードバックテストモード
              FB_VERTEX: 頂点を対象
              FB_FACE: 面を対象
              FB_EDGE: 辺を対象
        """
        if self._feedbackMode == fm: return
        if fm in (FB_VERTEX, FB_FACE, FB_EDGE):
            self._feedbackMode = fm
        return
    
    def getFeedbackMode(self):
        """
        フィードバックテストモードを返す
        """
        return self._feedbackMode

    def setLineStipple(self, lsType):
        """
        線種を設定する
        - lsType: 線種
                  ST_SOLID: 実戦
                  ST_DOT: 点線
                  ST_DASH: 破線
                  ST_DDASH1: 一点鎖線
                  ST_DDASH2: ニ点鎖線
        """
        if self._lineStipple == lsType: return
        self._lineStipple = lsType
        if self._renderMode & RT_WIRE :
            self.notice()

    def getLineStipple(self):
        """
        線種を返す
        """
        return self._lineStipple

    def setLineWidth(self, lw):
        """
        線幅を設定する
        - lw: 線幅(0.0〜)
        """
        if float(lw) < 0.0: return
        self._lineWidth = float(lw)
        if self._renderMode & RT_WIRE :
            self.notice()

    def getLineWidth(self):
        """
        線幅を返す
        """
        return self._lineWidth

    def setPointSymbol(self, psType):
        """
        ポイントタイプを設定する
        - psType: ポイントタイプ
                  SYM_NORMAL: 標準, SYM_PLUS: '＋', SYM_CROSS: '×',
                  SYM_CIRCLE: '◯', SYM_CIRCFILL: '●',
                  SYM_SQUARE: '□', SYM_SQUAFILL: '■',
                  SYM_TRIANGLE: '△', SYM_TRIAFILL: '▲'
        """
        if self._pointSymbol == psType: return
        self._pointSymbol = psType
        if self._renderMode & RT_POINT :
            self.notice()

    def getPointSymbol(self):
        """
        ポイントタイプを返す
        """
        return self._pointSymbol

    def setPointSize(self, ps):
        """
        ポイントサイズを設定する(ポイントタイプがSYM_NORMALの場合の)
        - ps: ポイントサイズ(0.0〜)
        """
        if float(ps) < 0.0: return
        self._pointSize = float(ps)
        if self._renderMode & RT_POINT :
            self.notice()

    def getPointSize(self):
        """
        ポイントサイズを返す
        """
        return self._pointSize

    def setSpecular(self, spc):
        """
        スペキュラー反射係数を設定する
        - spc: スペキュラー反射係数(RGBA: 0.0〜)
        """
        self._specular[0:4] = spc[0:4]
        if self._renderMode & (RT_SMOOTH|RT_FLAT):
            self.notice()

    def getSpecular(self):
        """
        スペキュラー反射係数を返す
        """
        return self._specular

    def setAmbient(self, amb):
        """
        環境光反射係数を設定する
        - amb: 環境光反射係数(RGBA: 0.0〜)
        """
        self._ambient[0:4] = amb[0:4]
        if self._renderMode & (RT_SMOOTH|RT_FLAT):
            self.notice()

    def getAmbient(self):
        """
        環境光反射係数を返す
        """
        return self._ambient

    def setShininess(self, shn):
        """
        反射指数を設定する
        - shn: 反射指数(0.0〜)
        """
        try:
            self._shinines[0] = shn
        except:
            self._shinines[0] = shn[0]
        if self._renderMode & (RT_SMOOTH|RT_FLAT):
            self.notice()

    def getShininess(self):
        """
        反射指数を返す
        """
        return self._shinines

    def setEmission(self, ems):
        """
        放射光係数を設定する
        - ems: 放射光係数(RGBA: 0.0〜)
        """
        self._emission[0:4] = ems[0:4]
        if self._renderMode & (RT_SMOOTH|RT_FLAT):
            self.notice()

    def getEmission(self):
        """
        放射光係数を返す
        """
        return self._emission

    def setTexture(self, tex):
        if self._texture == tex:
            return True
        self._texture = tex
        self._texture.setBbox(self._bbox[0], self._bbox[1])
        self.notice()
        return

    #-------- propagate interface --------
    def notice(self, invalidateDL =True):
        """
        変更通知
        表示内容が変更されたことを親ノードに通知します.
        - invalidateDL: ディスプレイリスト無効化フラグ
        """
        if invalidateDL:
            self.invalidateDispList()
        Node.notice(self)
        return

    def rumor(self, ref):
        """
        破壊通知の受付け
        本メソッドは、refのdestroyメソッドから自動的に呼び出されます.
        - ref: 破壊されたノード
        """
        Node.rumor(self, ref)
        return

    #-------- class methods --------
    def SetImmediateMode(cls, im):
        """
        イミディアットモード(ディスプレイリストを使用しない)の設定
        (クラスメソッド)
        - im: イミディアットモード
        """
        GfxNode._GfxNode__useDispList = not im
        return
    SetImmediateMode = classmethod(SetImmediateMode)

    def IsImmediateMode(cls):
        """
        イミディアットモードを返す
        (クラスメソッド)
        """
        return not GfxNode._GfxNode__useDispList
    IsImmediateMode = classmethod(IsImmediateMode)

