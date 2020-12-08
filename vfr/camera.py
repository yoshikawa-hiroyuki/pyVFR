#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from OpenGL.GL import *
from OpenGL.GLU import *
from .gfxGroup import *
from .frustum import *
from .scene import *
from .node import *
from .image import *
from .utilMath import *


#----------------------------------------------------------------------
class Camera(Base):
    """
    カメラクラス
    カメラを表わす基底クラスです.
    視垂台, シーン, 前面表示オブジェクトから構成されます.
      _scene: シーン
      _front: 前面表示オブジェクト
      _da: ウインドウ描画領域
      _selected: セレクションテスト結果
      _feedbacked: フィードバックテスト結果
      _antiAlias: アンチエイリアシングモード
      _bgColor: 背景色(RGBA)
      _bgImage: 背景画像
      _frustum: 視垂台
      _fogMode: フォグモード
      _fogStart, _fogEnd: フォグパラメータ
      _clickSpotSize: クリックセレクション/フィードバックテストスポットサイズ
    """
    def __init__(self, suicide =False):
        Base.__init__(self, suicide)
        self._scene = None
        self._front = None
        self._da = None
        self._selected = []
        self._feedbacked = []
        self._antiAlias = True
        self._bgColor = [0.0, 0.0, 0.0, 1.0]
        self._bgImage = None
        self._frustum = Frustum()
        self._fogMode = False
        self._fogStart = 9.0
        self._fogEnd = 15.0
        self._clickSpotSize = 5

    def __del__(self):
        Base.__del__(self)

    def destroy(self):
        self.relaxSelect()
        self.relaxFeedback()
        self.setDrawArea(None)
        self.setScene(None)
        self.setFrontNode(None)
        Base.destroy(self)

    def redraw(self, asp =1.0):
        """
        描画
        シーンおよび前面表示オブジェクトをOpenGLで描画します.
        - asp: 視界のアスペクト比(横/縦)
        """
        if self._scene == None: return

        # Background Painting
        self.bgPaint()

        # Set OpenGL modes
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LINE_STIPPLE)

        # Lighting Model
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        # AntiAlias Lines
        if self._antiAlias:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POINT_SMOOTH)
        else:
            glDisable(GL_LINE_SMOOTH)
            glDisable(GL_POINT_SMOOTH)

        # Fog
        if self._fogMode:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_LINEAR)
            glFogfv(GL_FOG_COLOR, self._bgColor)
            glFogf(GL_FOG_START, self._fogStart)
            glFogf(GL_FOG_END, self._fogEnd)
        else:
            glDisable(GL_FOG)
        glHint(GL_FOG_HINT, GL_FASTEST)

        # Polygon Offset
        glPolygonOffset(1.0, 0.000001)
        glEnable(GL_POLYGON_OFFSET_FILL)

        # Camera Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.projection(asp)

        # Initialize Model Coordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._frustum.ApplyModelview()

        # Scene Rendering
        if not self._scene == None:
            self._scene.render()

        # FrontObj Rendering
        self.fgPaint()

        # Relax AntiAlias mode
        if self._antiAlias:
            glDisable(GL_LINE_SMOOTH)

    def setScene(self, scene):
        """
        シーンの設定
        - scene: 描画対象シーン
        """
        if self._scene:
            self._scene.remRef(self)
        self._scene = scene
        if self._scene:
            self._scene.addRef(self)
        self.notice()

    def setFrontNode(self, fobj):
        """
        前面表示オブジェクトの設定
        - fobj: 前面表示オブジェクト
        """
        if self._front:
            self._front.remRef(self)
        self._front = fobj
        if self._front:
            self._front.addRef(self)
        self.notice()

    def setBgImage(self, bgi):
        """
        背景画像の設定
        - bgi: 背景画像
        """
        if self._bgImage:
            self._bgImage.remRef(self)
        self._bgImage = bgi
        if self._bgImage:
            self._bgImage.addRef(self)
        self.notice()

    def setDrawArea(self, da):
        """
        DrawArea(描画領域)の設定
        本メソッドは、drawArea::setScene()メソッドから自動的に呼ばれます.
        - da: DrawArea
        """
        if self._da == da:
            return
        if self._da:
            self._da.rumor()
        self._da = da
        self.notice()
        
    setScreen = setDrawArea

    def getProjMatrix(self, asp =1.0):
        """
        プロジェクション行列を返す
        - asp: 視界のアスペクト比(横/縦)
        """
        return self._frustum.GetPM(self.getProjection()==PR_ORTHOGONAL, asp)

    def getModelMatrix(self):
        """
        モデルビュー行列を返す
        """
        return self._frustum.GetMVM()

    def setBgColor(self, bgc):
        """
        背景色の設定
        - bgc: 背景色(RGBA)
        """
        self._bgColor[0:] = bgc[0:]
        self.notice()

    def setFogMode(self, mode):
        """
        フォグモードの設定
        - mode: フォグモード
        """
        if self._fogMode == f: return
        self._fogMode = mode
        self.notice()

    def setFogParam(self, start, end):
        """
        フォグパラメータの設定
        - start: フォグ開始距離
        - end: フォグ終了距離
        """
        self._fogStart = start
        self._fogEnd = end
        if self._fogMode:
            self.notice()

    def setProjection(self, proj):
        """
        プロジェクションモードの設定
        本メソッドは、Camera3D派生クラス用の仮想メソッドです.
        - proj: プロジェクションモード(PR_PERSPECTIVEまたはPR_ORTHOGONAL)
        """
        pass

    def getProjection(self):
        """
        プロジェクションモードを返す
        本メソッドは、Camera3D派生クラス用の仮想メソッドです.
        """
        return PR_ORTHOGONAL

    def setClickSpotSize(self, size):
        """
        クリック操作のスポットサイズを設定します.
        - size: スポットサイズ(ピクセル)
        """
        if size < 1: return
        self._clickSpotSize = size

    def clickSelect(self, cx, cy):
        """
        マウスクリックによるセレクションテストを実行します.
        - cx: クリックポイントのX座標
        - cy: クリックポイントのY座標
        """
        self.relaxSelect()
        if self.selection(cx, cy, self._clickSpotSize,self._clickSpotSize) < 1:
            return []
        return self._selected

    def sweepSelect(self, x, y, w, h):
        """
        マウススィープによるセレクションテストを実行します.
        - x: スィープ開始点のX座標
        - y: スィープ開始点のY座標
        - w: スィープ領域の幅(ピクセル)
        - h: スィープ領域の高さ(ピクセル)
        """
        (ww, hh) = (w, h)
        if w < self._clickSpotSize: ww = self._clickSpotSize
        if h < self._clickSpotSize: hh = self._clickSpotSize
        cx = x + w/2
        cy = y + h/2
        self.relaxSelect()
        if self.selection(cx, cy, ww, hh) < 1:
            return []
        return self._selected

    def clickFeedback(self, cx, cy, target):
        """
        マウスクリックによるフィードバックテストを実行します.
        - cx: クリックポイントのX座標
        - cy: クリックポイントのY座標
        """
        self.relaxFeedback()
        if self.feedback(cx, cy, self._clickSpotSize, self._clickSpotSize,
                         target) < 1:
            return []
        return self._feedbacked

    def sweepFeedback(self, x, y, w, h, target):
        """
        マウススィープによるフィードバックテストを実行します.
        - x: スィープ開始点のX座標
        - y: スィープ開始点のY座標
        - w: スィープ領域の幅(ピクセル)
        - h: スィープ領域の高さ(ピクセル)
        """
        (ww, hh) = (w, h)
        if w < self._clickSpotSize: ww = self._clickSpotSize
        if h < self._clickSpotSize: hh = self._clickSpotSize
        cx = x + w/2
        cy = y + h/2
        self.relaxFeedback()
        if self.feedback(cx, cy, ww, hh, target) < 1:
            return []
        return self._feedbacked 

    def relaxSelect(self):
        """
        セレクションテスト結果バッファをクリアします.
        """
        self._selected = []

    def relaxFeedback(self):
        """
        フィードバックテスト結果バッファをクリアします.
        """
        self._feedbacked = []

    def getFocusDepth(self):
        """
        モデル座標・スクリーン座標変換用のデプス値を返します.
        """
        d = self._frustum._dist / (self._frustum._far - self._frustum._near)
        return d

    def setOrthoHint(self, h):
        """
        ビューポート比(横/縦)を設定します.
        """
        if h < EPSF: return
        self._frustum._halfW *= (h / self._frustum._halfH)
        self._frustum._halfH = h
        self.notice()

    def dragRot(self, dx, dy):
        """
        マウスドラッグによる視線方向の回転
        - dx: マウス移動量のX成分
        - dy: マウス移動量のY成分
        """
        if self._da == None: return
        Viewp = self._da._viewport
        if Viewp[2] > Viewp[3]:
            l = Viewp[2] / 2
        else:
            l = Viewp[3] / 2
        if l < 1: return
        rx = dx * 45.0 / l
        ry = dy * 45.0 / l
        if dx != 0.0: self._frustum._hpr.m_v[0] += rx
        if dy != 0.0: self._frustum._hpr.m_v[1] += ry
        self.notice()

    def dragTrans(self, dx, dy):
        """
        マウスドラッグによる視点の平行移動
        - dx: マウス移動量のX成分
        - dy: マウス移動量のY成分
        """
        if dx == 0.0 and dy == 0.0: return
        if self._da == None: return
        Viewp = self._da._viewport
        if Viewp[3] < 1: return
        tx = -2 * self._frustum._halfH * dx / Viewp[3]
        ty =  2 * self._frustum._halfH * dy / Viewp[3]
        (x0, y0) = (Vec3((1,0,0)), Vec3((0,1,0)))
        RM = Mat4()
        RM.RotY(Deg2Rad(self._frustum._hpr.m_v[0]))
        RM.RotX(Deg2Rad(self._frustum._hpr.m_v[1]))
        RM.RotZ(Deg2Rad(self._frustum._hpr.m_v[2]))
        x1 = RM * x0
        y1 = RM * y0
        x1 = x1 * tx
        y1 = y1 * ty
        self._frustum._eye = self._frustum._eye + x1
        self._frustum._eye = self._frustum._eye + y1
        self.notice()

    def dragTransZ(self, dx, dy):
        """
        マウスドラッグによる視点の前後移動
        - dx: マウス移動量のX成分
        - dy: マウス移動量のY成分
        """
        if dy == 0.0: return
        if self._da == None: return
        Viewp = self._da._viewport
        if Viewp[3] < 1: return
        tz = 2 * self._frustum._halfH * dy / Viewp[3]
        RM = Mat4()
        RM.RotY(Deg2Rad(self._frustum._hpr.m_v[0]))
        RM.RotX(Deg2Rad(self._frustum._hpr.m_v[1]))
        RM.RotZ(Deg2Rad(self._frustum._hpr.m_v[2]))
        dz = RM * Vec3((0, 0, tz))
        self._frustum._eye = self._frustum._eye + dz
        self.notice()

    def rotx(self, r):
        """
        視線方向のX軸回り回転
        - r: 回転角(rad)
        """
        self._frustum._hpr.m_v[1] += Rad2Deg(r)
        self.notice()
    def roty(self, r):
        """
        視線方向のY軸回り回転
        - r: 回転角(rad)
        """
        self._frustum._hpr.m_v[0] += Rad2Deg(r)
        self.notice()
    def rotz(self, r):
        """
        視線方向のZ軸回り回転
        - r: 回転角(rad)
        """
        self._frustum._hpr.m_v[2] += Rad2Deg(r)
        self.notice()
    def rotation(self, a, v):
        """
        視線方向の任意軸回り回転
        本メソッドは無効です.
        - a: 回転軸
        - v: 回転角(rad)
        """
        pass

    def scale(self, v):
        """
        視界のスケーリング
        本メソッドは無効です.
        - v: スケーリングファクター
        """
        pass

    def trans(self, v):
        """
        視界の平行移動
        - v: 平行移動量
        """
        self._frustum._eye = self._frustum._eye + v
        self.notice()

    def identity(self):
        """
        視界変換の初期化
        """
        self.resetTrans()

    def getNodeById(self, id):
        """
        IDによるノード検索
        シーンおよび前面表示オブジェクトから、指定されたIDのノードを検索します.
        - id: 検索するノードID
        """
        if self._scene: pnode = self._scene.getNodeById(id)
        if pnode != None: return pnode
        if self._front: pnode = self._front.getNodeById(id)
        if pnode != None: return pnode
        if self._bgImage: pnode = self._bgImage.getNodeById(id)
        if pnode != None: return pnode
        return None

    def getNodeByName(self, name):
        """
        名前によるノード検索
        シーンおよび前面表示オブジェクトから、指定された名前のノードを検索し、
        最初に見つかったノードを返します.
        - name: 検索するノードの名前
        """
        if self._scene: pnode = self._scene.getNodeByName(name)
        if pnode != None: return pnode
        if self._front: pnode = self._front.getNodeByName(name)
        if pnode != None: return pnode
        if self._bgImage: pnode = self._bgImage.getNodeByName(name)
        if pnode != None: return pnode
        return None

    def accumMatrix(self, tid, M):
        """
        幾何変換行列の累積演算
        指定されたIDを持つノードまでの幾何変換行列の累積演算を行い、
        Mに適用します.
        シーン配下に指定されたIDを持つノードが存在しない場合はFalseを返します.
        - tid: ターゲットノードのID
        - M: 幾何変換行列
        """
        if self._scene == None: return False
        M1 = M * self.getModelMatrix()
        self._scene.accumMatrix(tid, M1)
        M.m_v[0:] = M1.m_v[0:]
        return True

    def rumor(self, ref):
        """
        破壊通知の受付け
        本メソッドは、シーンおよび前面表示オブジェクトのdestroyメソッドから
        自動的に呼び出されます.
        - ref: 破壊されたノード
        """
        if ref == None: return
        if ref == self._front:
            self._front = None
            self.notice()
            return
        if ref == self._bgImage:
            self._bgImage = None
            self.notice()
            return
        if ref == self._scene:
            self._scene = None
            self.notice()
            return

    def notice(self, invalidateDL =True):
        """
        変更通知
        表示内容が変更されたことをDrawAreaに通知します.
        - invalidateDL: ディスプレイリスト無効化フラグ
        """
        if self._da:
            self._da.notice(invalidateDL)

    def chkNotice(self):
        """
        再描画チェック
        表示内容の変更が発生していた場合、DrawAreaが再描画を実行します.
        """
        if self._da:
            self._da.chkNotice()

    def clearDispList(self):
        """
        OpenGLディスプレイリストの破棄
        再起的に全てのノードのOpenGLディスプレイリストを破棄します.
        """
        self._scene.clearDispList()
        self._front.clearDispList()
        self._bgImage.clearDispList()

    def sweepZoom(self, p0, p1):
        """
        マウススィープによるズーム
        派生クラスで実装されます.
        """
        pass

    def resetTrans(self):
        """
        視界の幾何変換をリセットします.
        """
        self._frustum._eye = Vec3((0, 0, self._frustum._dist))
        self._frustum._hpr = Vec3()
        self.notice()

    def bgPaint(self):
        """
        背景塗りつぶし
        """
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glPolygonMode(GL_FRONT, GL_FILL)

        if self._bgImage and self._bgImage.isDrawable():
            Viewp = self._da._viewport
            self._bgImage.fitSize[0] = Viewp[2]
            self._bgImage.fitSize[1] = Viewp[3]
            self._bgImage.renderSolid()
        else:
            glColor4fv(self._bgColor)
            glBegin(GL_POLYGON)
            glVertex2f(-1.0, -1.0)
            glVertex2f( 1.0, -1.0)
            glVertex2f( 1.0,  1.0)
            glVertex2f(-1.0,  1.0)
            glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def fgPaint(self):
        """
        前面表示オブジェクトの描画
        """
        if self._front == None: return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        psz = self._da.getSize()
        if psz.y <= 0:
            asp = 1.0
        else:
            asp = float(psz.x) / float(psz.y)
            glOrtho(-asp, asp, -1.0, 1.0, -50.0, 50.0)

        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_LIGHT0)
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
        glDisable(GL_LIGHT3)
        positionPara = [0.0, 0.0, 1.0, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, positionPara)

        # Non-Transparent front-object
        self._front.render_(False)

        # Transparent front-object
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._front.render_(True)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def projection(self, aspect):
        """
        投影変換
        派生クラスで実装されます.
        """
        pass

    def selection(self, cx, cy, w, h):
        """
        セレクションテスト
        セレクションテストを実行し、ヒットしたノード数を返します.
        エラーの場合は-1を返します.
        セレクション領域はスクリーン座標((0,0)は描画領域の左上隅)で指定します.
        セレクションテストの結果は_selectedに格納されます．
        - cx: セレクション領域の中心のX座標
        - cy: セレクション領域の中心のY座標
        - w: セレクション領域の幅
        - h: セレクション領域の高さ
        """
        # not relaxed
        if len(self._selected) > 0: return -1

        # Get Viewport of Screen
        if self._da == None: return -1
        Viewp = self._da._viewport
        x = Viewp[0] + cx
        y = Viewp[1] + Viewp[3] - cy

        selectBufSize = (Node._sequence % 20000) * 5
        glSelectBuffer(selectBufSize)

        glRenderMode(GL_SELECT)
        glInitNames()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPickMatrix(x, y, w, h, Viewp)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.projection(float(Viewp[2])/float(Viewp[3]))
        self._frustum.ApplyModelview()

        if self._scene:
            self._scene.render()

        if self._front:
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            psz = self._da.getSize()
            if psz.y <= 0: asp = 1.0
            else:          asp = float(psz.x) / float(psz.y)
            glOrtho(-asp, asp, -1.0, 1.0, -50.0, 50.0)
            self._front.render_(False)
            self._front.render_(True)
            glPopMatrix()

        glFlush()

        """ glGetError not ported to PyOpenGL, raise exception.
        """

        selectBuf = glRenderMode(GL_RENDER)
        hits = len(selectBuf)
        if hits < 1: return 0
        self._selected = [0 for i in range(hits)]
        depthL = [[0.0, 0] for i in range(hits)] # [depth, id]

        i = 0
        for hit_record in selectBuf:
            min_depth, max_depth, names = hit_record
            depthL[i][0] = min_depth # this is depth1
            depthL[i][1] = names[-1]
            i += 1
        depthL.sort()

        for i in range(hits):
            self._selected[i] = depthL[i][1]
        
        del depthL, selectBuf
        return len(self._selected)

    def feedback(self, cx, cy, w, h, target):
        """do OpenGL feedback
        フィードバックテスト
        フィードバックテストを実行し、ヒットしたエレメント数を返します.
        エラーの場合は-1を返します.
        フィードバック領域はスクリーン座標((0,0)は描画領域の左上隅)で
        指定します.
        フィードバックテストの結果は_feedbackedに格納されます．
        - cx: フィードバック領域の中心のX座標
        - cy: フィードバック領域の中心のY座標
        - w: フィードバック領域の幅
        - h: フィードバック領域の高さ
        - target: フィードバック対象ノードのID
        """

        # not relaxed
        if len(self._feedbacked) > 0: return -1

        # Get Viewport of Screen
        if self._da == None: return -1
        Viewp = self._da._viewport
        x = Viewp[0] + cx
        y = Viewp[1] + Viewp[3] - cy

        # Alloc FeedBack Buffer
        tobj = self.getNodeById(target)
        if tobj == None: return -1
        NumVerts = tobj.getNumVerts()
        NumIndices = tobj.getNumIndices()
        if NumVerts < 1 and NumIndices < 1: return 0
        feedBufSize = tobj.getFeedbackSize()
        fbkType = tobj._feedbackMode

        # Go FeedBack
        glFeedbackBuffer(feedBufSize, GL_3D)
        glRenderMode(GL_FEEDBACK)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPickMatrix(x, y, w, h, Viewp)
        self.projection(float(Viewp[2])/float(Viewp[3]))

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._frustum.ApplyModelview()

        if self._scene:
            self._scene.renderFeedBack(target)

        if self._front:
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            psz = self._da.getSize()
            if psz.y <= 0: asp = 1.0
            else:          asp = float(psz.x) / float(psz.y)
            glOrtho(-asp, asp, -1.0, 1.0, -50.0, 50.0)
            self._front.renderFeedBack(target)
            glPopMatrix()

        glFlush()

        """ glGetError not ported to PyOpenGL, raise exception.
        """

        feedBuf = glRenderMode(GL_RENDER)
        hits = len(feedBuf)
        if hits < 1: return 0

        count = 0
        for x in feedBuf:
            token = x[0]
            value = x[1:]
            if (token == GL_POINT_TOKEN and fbkType == FB_VERTEX) or \
                    (token == GL_LINE_TOKEN and fbkType == FB_EDGE) or \
                    (token == GL_LINE_RESET_TOKEN and fbkType == FB_EDGE) or \
                    (token == GL_POLYGON_TOKEN and fbkType == FB_FACE) :
                count += 1
        if count < 1: return 0
  
        distbuf = {}
        getPath = False
        getId = -1
        for x in feedBuf:
            token = x[0]
            value = x[1:]
            if token == GL_PASS_THROUGH_TOKEN:
                getPath = True
                getId = int(value[0])
            elif getPath and getId >= 0 and ( \
                (token == GL_POINT_TOKEN and fbkType == FB_VERTEX) or
                (token == GL_LINE_TOKEN and fbkType == FB_EDGE) or
                (token == GL_LINE_RESET_TOKEN and fbkType == FB_EDGE) or
                (token == GL_POLYGON_TOKEN and fbkType == FB_FACE) ):
                if fbkType == FB_VERTEX:
                    distbuf[getId] = value[0].vertex[2]
                elif fbkType == FB_EDGE:
                    distbuf[getId] = (value[0].vertex[2]
                                      + value[1].vertex[2]) * 0.5
                elif fbkType == FB_FACE and len(value) > 0:
                    zval = 0.0
                    for v in value:
                        zval += v.vertex[2]
                    distbuf[getId] = zval / len(value)
                else:
                    distbuf[getId] = 1.0
                getPath = False
                getId = -1
            else:
                getPath = False
                getId = -1
        distbuf = list(zip(distbuf.values(), distbuf.keys()))
        distbuf.sort()

        self._feedbacked = [0 for i in range(len(distbuf))]
        for i in range(len(self._feedbacked)):
            self._feedbacked[i] = distbuf[i][1]
        del distbuf, feedBuf
        return len(self._feedbacked)


#----------------------------------------------------------------------
VIEW3D_CLIP_NEAR     = 0.1
VIEW3D_CLIP_FAR      = 1000.1
VIEW3D_FIELD_OF_VIEW = 45.0
VIEW3D_WIDE_HALF     = 5.0
PI_PER_180           = 0.017453293

class Camera3D(Camera):
    """
    3Dカメラクラス
    透視投影および平行投影をサポートするカメラクラスです.
    """
    def __init__(self, suicide =False):
        Camera.__init__(self, suicide)
        self._projMode = PR_PERSPECTIVE

    def setProjection(self, proj):
        """
        プロジェクションモードの設定
        -proj: プロジェクションモード(PR_PERSPECTIVEまたはPR_ORTHOGONAL)
        """
        self._projMode = proj
        self.notice()
        
    def getProjection(self):
        """
        プロジェクションモードを返す
        """
        return self._projMode
    
    def projection(self, aspect):
        """
        投影変換
        - aspect: 描画領域のアスペクト比(横/縦)
        """
        self._frustum.ApplyProjection((self._projMode==PR_ORTHOGONAL), aspect)

    def setHpr(self, h, p, r):
        """
        視線方向の設定
        - h: Y軸回りの回転量(deg)
        - p: X軸回りの回転量(deg)
        - r: Z軸回りの回転量(deg)
        """
        self._frustum._hpr.m_v[0] += h
        self._frustum._hpr.m_v[1] += p
        self._frustum._hpr.m_v[2] += r
        self.notice()

    def sweepZoom(self, p0, p1):
        """
        マウススィープによるズーム
        - p0: スイープ領域の開始点座標
        - p1: スイープ領域の終了点座標
        """
        nW = abs(p1.x - p0.x)
        nH = abs(p1.y - p0.y)
        if nW < 5 or nH < 5: return False
        target = self._scene
        if target == None: return False
        ds = self._da
        if da == None: return False
        oVP = da._viewport
        MVM = self._frustum.GetMVM()

        # Center Point
        so0 = Point2(oVP[2] / 2, oVP[3] / 2)
        so1 = (p0 + p1) * 0.5
        (vo0, vo1, vW) = (Vec3(), Vec3(), Vec3())
        vO = Vec3()
        da.getObjCoord(target.getID(), so0, vO)
        vW = vO
        vo0 = MVM * vW
        da.getObjCoord(target.getID(), so1, vO)
        vW = vO
        vo1 = MVM * vW
        vD = Vec3(vo1-vo0[0])
        self.trans(vD)

        if self._projMode == PR_ORTHOGONAL:
            # Viewport Size
            oH = self._frustum._halfH
            oH2 = oH
            if nW > nH:
                oH2 *= float(nW) / oVP[2]
            else:
                oH2 *= float(nH) / oVP[3]
            if oH2 > EPSF:
                self.setOrthoHint(oH2)

            # Close to Focus (for Perspective)
            fe = Vec3((0,0,-1))
            MVRM = self._frustum.GetMVRM()
            fe = (MVRM * fe).unit()
            L1 = self._frustum._dist
            L2 = L1 * (1.0 - float(oH2 / oH))
            fe = fe * L2
            self._frustum._eye = self._frustum._eye + fe
            self.setFogParam(L1, L1*2)
        return True


#----------------------------------------------------------------------
VIEW2D_DEPTH_HALF = 1000.0
VIEW2D_WIDE_HALF  = 5.0

class Camera2D(Camera):
    """
    2Dカメラクラス
    平行投影のみをサポートするカメラクラスです.
    視界の回転変換は行えません.
    """
    def __init__(self, suicide =False):
        Camera.__init__(self, suicide)

    def projection(self, aspect):
        """
        投影変換
        - aspect: 描画領域のアスペクト比(横/縦)
        """
        self._frustum.ApplyProjection(True, aspect)

    def dragRot(self, dx, dy):
        """
        マウスドラッグによる視線方向の回転
        本クラスでは無効です.
        """
        pass

    def dragTrans(self, dx, dy):
        """
        マウスドラッグによる視点の平行移動
        - dx: マウス移動量のX成分
        - dy: マウス移動量のY成分
        """
        if dx == 0.0 and dy == 0.0:
            return
        da = self._da
        if da == None:
            return
        scrnSize = da.getSize()
        if scrnSize.y < 1:
            return
        tx = -2 * self._frustum._halfH * dx / scrnSize.y
        ty =  2 * self._frustum._halfH * dy / scrnSize.y
        tv = Vec3((tx, ty, 0.0))
        self.trans(tv)

    def dragTransZ(self, dx, dy):
        """
        マウスドラッグによる視点の前後移動
        - dx: マウス移動量のX成分
        - dy: マウス移動量のY成分
        """
        if dy == 0.0: return
        da = self._da
        if da == None: return
        scrnSize = da.getSize()
        if scrnSize.y < 1: return
        if dy < 0.0:
            s = 0.5 * dy / (scrnSize.y*0.5) + 1.0
        else:
            s = dy / (scrnSize.y*0.5) + 1.0
        self.setOrthoHint(self._frustum._halfH * s)

    def rotx(self, r):
        """
        視線方向のX軸回り回転
        本クラスでは無効です.
        """
        pass

    def roty(self, r):
        """
        視線方向のY軸回り回転
        本クラスでは無効です.
        """
        pass

    def rotz(self, r):
        """
        視線方向のZ軸回り回転
        本クラスでは無効です.
        """
        pass

    def rotation(self, a, v):
        """
        視線方向の任意軸回り回転
        本クラスでは無効です.
        """
        pass

    def sweepZoom(self, p0, p1):
        """
        マウススィープによるズーム
        - p0: スイープ領域の開始点座標
        - p1: スイープ領域の終了点座標
        """
        nW = abs(p1.x - p0.x)
        nH = abs(p1.y - p0.y)
        if nW < 5 or nH < 5: return False
        target = self._scene
        if target == None: return False
        da = self._da
        if da == None: return False
        oVP = da._viewport

        # Center Point
        so0 = Point2(oVP[0] + oVP[2]/2, oVP[1] + oVP[3]/2)
        so1 = (p0 + p1) * 0.5
        (vo0, vo1) = (Vec3(), Vec3())
        da.getObjCoord(target.getID(), so0, vo0)
        da.getObjCoord(target.getID(), so1, vo1)
        vD = Vec3(vo1[0]-vo0[0], vo1[1]-vo0[1], vo1[2]-vo0[2])
        self.trans(vD)

        # Viewport Size
        oH = self._frustum._halfH
        if nW > nH:
            oH *= float(nW) / oVP[2]
        else:
            oH *= float(nH) / oVP[3]
        if oH > EPSF:
            self.setOrthoHint(oH)
        return True
