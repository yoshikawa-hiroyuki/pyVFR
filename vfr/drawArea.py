#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import math
import numpy as N
import ctypes as C
from OpenGL.GL import *
from OpenGL.GLU import *
from .gfxNode import *
from .events import *
from .utilMath import *
import platform

#----------------------------------------------------------------------
import os.path
vfr_impl = N.ctypeslib.load_library('vfr_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))

vfr_impl.drawArea_DragRotMatrix.restype = C.c_int
vfr_impl.drawArea_DragRotMatrix.argtypes = [
    C.POINTER(C.c_float), C.POINTER(C.c_float), C.POINTER(C.c_float),
    C.c_float, C.POINTER(C.c_int), C.POINTER(C.c_int), C.POINTER(C.c_int)]

vfr_impl.drawArea_DragTransMatrix.restype = C.c_int
vfr_impl.drawArea_DragTransMatrix.argtypes = [
    C.POINTER(C.c_float), C.POINTER(C.c_float), C.POINTER(C.c_float),
    C.c_float, C.POINTER(C.c_int), C.POINTER(C.c_int), C.POINTER(C.c_int)]

vfr_impl.drawArea_DragScaleMatrix.restype = C.c_int
vfr_impl.drawArea_DragScaleMatrix.argtypes = [
    C.POINTER(C.c_float), C.POINTER(C.c_int),
    C.POINTER(C.c_int), C.POINTER(C.c_int)]


#----------------------------------------------------------------------
class DrawArea(object):
    """
    描画領域クラス
    DrawAreaは描画領域機能を定義する基底クラスです。
    メンバーとしてカメラを持ち、描画領域内にOpenGLによる描画を行います。
    また、描画領域で発生する各種イベント(Windowsではメッセージ)を、
    クラス内部のイベントハンドラーで処理し、独自の仮想イベントとして
    再構成します。
      _camera: シーングラフ・カメラノード
      _viewport: ビューポート
      _evtTable: 仮想イベントテーブル
      rb_xxx: ラバーバンドデータ
      _rb_xxx: ラバーバンド描画データ
    """

    """内部イベント状態タイプ"""
    (WaitAny,
     LBPressed, LDraggingSolo, LDraggingShift,
     LDraggingCntl, LDraggingShiftCntl,
     RBPressed, RDraggingSolo, RDraggingShift,
     RDraggingCntl, RDraggingShiftCntl,
     MBPressed, MDraggingSolo, MDraggingShift,
     MDraggingCntl, MDraggingShiftCntl, MouseWheel) = range(17)
     
    def __init__(self):
        # rubber-box datas
        self.rb_flag = False
        self.rb_0 = Point2()
        self.rb_sz = Point2()
        self.rb_color = [0.9, 0.9, 0.9, 1.0]
        self.rb_lineWidth = 2.0
        self.rb_lineType = ST_SOLID

        # screen
        self._camera = None
        self._viewport = [0, 0, 100, 100]
        self._rb0 = Point2()
        self._rb1 = Point2()

        # events
        self._evtTable = {
            EVT_KeyIn:EvKeyIn(self),
            
            EVT_Click:EvClick(self),
            EVT_DragStart:EvDragStart(self),
            EVT_DragEnd:EvDragEnd(self),
            EVT_Drag:EvDrag(self),
            EVT_SClick:EvClick(self, shift=True),
            EVT_SDragStart:EvDragStart(self, shift=True),
            EVT_SDragEnd:EvDragEnd(self, shift=True),
            EVT_SDrag:EvDrag(self, shift=True),
            EVT_CClick:EvClick(self, control=True),
            EVT_CDragStart:EvDragStart(self, control=True),
            EVT_CDragEnd:EvDragEnd(self, control=True),
            EVT_CDrag:EvDrag(self, control=True),
            EVT_SCClick:EvClick(self, shift=True, control=True),
            EVT_SCDragStart:EvDragStart(self, shift=True, control=True),
            EVT_SCDragEnd:EvDragEnd(self, shift=True, control=True),
            EVT_SCDrag:EvDrag(self, shift=True, control=True),
            
            EVT_RClick:EvClick(self, EVT_MB_RIGHT),
            EVT_RDragStart:EvDragStart(self, EVT_MB_RIGHT),
            EVT_RDragEnd:EvDragEnd(self, EVT_MB_RIGHT),
            EVT_RDrag:EvDrag(self, EVT_MB_RIGHT),
            EVT_RSClick:EvClick(self, EVT_MB_RIGHT, shift=True),
            EVT_RSDragStart:EvDragStart(self, EVT_MB_RIGHT, shift=True),
            EVT_RSDragEnd:EvDragEnd(self, EVT_MB_RIGHT, shift=True),
            EVT_RSDrag:EvDrag(self, EVT_MB_RIGHT, shift=True),
            EVT_RCClick:EvClick(self, EVT_MB_RIGHT, control=True),
            EVT_RCDragStart:EvDragStart(self, EVT_MB_RIGHT, control=True),
            EVT_RCDragEnd:EvDragEnd(self, EVT_MB_RIGHT, control=True),
            EVT_RCDrag:EvDrag(self, EVT_MB_RIGHT, control=True),
            EVT_RSCClick:EvClick(self, EVT_MB_RIGHT, shift=True, control=True),
            EVT_RSCDragStart:EvDragStart(self,
                                         EVT_MB_RIGHT,shift=True,control=True),
            EVT_RSCDragEnd:EvDragEnd(self,
                                     EVT_MB_RIGHT, shift=True, control=True),
            EVT_RSCDrag:EvDrag(self, EVT_MB_RIGHT, shift=True, control=True),

            EVT_MClick:EvClick(self, EVT_MB_MIDDLE),
            EVT_MDragStart:EvDragStart(self, EVT_MB_MIDDLE),
            EVT_MDragEnd:EvDragEnd(self, EVT_MB_MIDDLE),
            EVT_MDrag:EvDrag(self, EVT_MB_MIDDLE),
            EVT_MSClick:EvClick(self, EVT_MB_MIDDLE, shift=True),
            EVT_MSDragStart:EvDragStart(self, EVT_MB_MIDDLE, shift=True),
            EVT_MSDragEnd:EvDragEnd(self, EVT_MB_MIDDLE, shift=True),
            EVT_MSDrag:EvDrag(self, EVT_MB_MIDDLE, shift=True),
            EVT_MCClick:EvClick(self, EVT_MB_MIDDLE, control=True),
            EVT_MCDragStart:EvDragStart(self, EVT_MB_MIDDLE, control=True),
            EVT_MCDragEnd:EvDragEnd(self, EVT_MB_MIDDLE, control=True),
            EVT_MCDrag:EvDrag(self, EVT_MB_MIDDLE, control=True),
            EVT_MSCClick:EvClick(self,
                                 EVT_MB_MIDDLE, shift=True, control=True),
            EVT_MSCDragStart:EvDragStart(self, EVT_MB_MIDDLE,
                                         shift=True, control=True),
            EVT_MSCDragEnd:EvDragEnd(self, EVT_MB_MIDDLE,
                                     shift=True, control=True),
            EVT_MSCDrag:EvDrag(self, EVT_MB_MIDDLE, shift=True, control=True),

            EVT_Wheel:EvWheel(self),

            EVT_Size:EvSize(self), EVT_Paint:EvPaint(self),
        }

    def getEvent(self, evt):
        """
        指定されたイベントデータを返す
        - evt: イベント種別
        """
        return self._evtTable[evt]

    def redraw(self):
        """
        再描画を行う
        派生クラスで実装されます．
        """
        self.getEvent(EVT_Paint).execAction()
    
    def notice(self, invalidateDL =True):
        """
        描画内容の変更通知を行う
        派生クラスで実装されます
        """
        pass
    
    def rumor(self):
        """
        カメラからの破壊通知を受付ける
        派生クラスで実装されます
        """
        pass
    
    def chkNotice(self):
        """
        描画内容の変更検査を行う
        派生クラスで実装されます
        """
        pass
    
    def getSize(self):
        """
        描画領域のサイズ(pixels)を返す
        派生クラスで実装されます
        """
        return Point2()

    def drawRB(self, p0, p1):
        """
        描画領域内にラバーボックスを描く
        - p0: ラバーボックスの始点座標
        - p1: ラバーボックスの終点座標
        """
        d = p1 - p0
        if d.x < 0:
            self.rb_0.x = p1.x
            self.rb_sz.x = -d.x
        else:
            self.rb_0.x = p0.x
            self.rb_sz.x = d.x
        if d.y < 0:
            self.rb_0.y = p1.y
            self.rb_sz.y = -d.y
        else:
            self.rb_0.y = p0.y
            self.rb_sz.y = d.y
        self.rb_flag = not self.rb_flag
        self.notice()

    def setRubberBoxColor(self, rbc):
        """
        ラバーボックスの色を設定する
        - rbc: ラバーボックスの色(rgba)
        """
        self.rb_color[0:] = rbc[0:]

    def setRubberBoxLineWidth(self, rblw):
        """
        ラバーボックスの線幅を設定する
        - rblw: ラバーボックスの線幅(pixel)
        """
        self.rb_lineWidth = rblw

    def setRubberBoxLineType(self, rblt):
        """
        ラバーボックスの線種を設定する
        - rblt: ラバーボックスの線種
        """
        self.rb_lineType = rblt

    def rb_draw(self):
        """
        描画領域内にラバーボックスをOpenGLで描画する
        """
        if not self.rb_flag: return
        sz = self.getSize()
        glViewport(0, 0, sz.x, sz.y)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor4fv(self.rb_color)
        glLineWidth(self.rb_lineWidth)
        if self.rb_lineType != ST_SOLID:
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1,GfxNode._GfxNode__stipplePattern[self.rb_lineType])

        (p0, p1) = (Point2(), Point2())
        p0[0] = 2.0 * self.rb_0.x / sz.x  - 1.0
        p0[1] = 2.0 * (sz.y - self.rb_0.y) / sz.y - 1.0
        p1[0] = 2.0 * (self.rb_0.x + self.rb_sz.x) / sz.x  - 1.0
        p1[1] = 2.0 * (sz.y - self.rb_0.y - self.rb_sz.y) / sz.y - 1.0

        glBegin(GL_LINE_STRIP)
        glVertex2f(p0[0], p0[1])
        glVertex2f(p1[0], p0[1])
        glVertex2f(p1[0], p1[1])
        glVertex2f(p0[0], p1[1])
        glVertex2f(p0[0], p0[1])
        glEnd()

        if self.rb_lineType != ST_SOLID:
            glDisable(GL_LINE_STIPPLE)
        return

    # screen
    def resized(self):
        """
        サイズ変更後処理
        描画領域のビューポートを再設定します．
        """
        size = self.getSize()
        self._viewport[0] = 0
        self._viewport[1] = 0
        self._viewport[2] = size.x
        self._viewport[3] = size.y
        if platform.system() == 'Darwin':
            try:
                import glfw
                glfw.init()
                win = glfw.create_window(size.x, size.y, 'check', None, None)
                fbsz = glfw.get_framebuffer_size(win)
                glfw.window_should_close(win)
                glfw.terminate()
                self._viewport[2] = fbsz[0]
                self._viewport[3] = fbsz[1]
            except:
                pass
            self.notice()

        self.getEvent(EVT_Size).execAction()
        return
    
    def setCamera(self, camera):
        """
        カメラを設定する
        - camera: カメラ
        """
        if self._camera:
            self._camera.setScreen(None)
        self._camera = camera
        if self._camera:
            self._camera.setScreen(self)
        self.notice()
        return
    
    def getCamera(self):
        """
        設定されているカメラを返す
        """
        return self._camera
    
    def clickSelect(self, cx, cy):
        """
        マウスクリックによるセレクションテスト
        - cx: クリックポイント(X座標)
        - cy: クリックポイント(Y座標)
        """
        if self._camera:
            return self._camera.clickSelect(cx, cy)
        return ()
    
    def sweepSelect(self, cx, cy, w, h):
        """
        マウススウィープによるセレクションテスト
        - cx: スウィープセンター(X座標)
        - cy: スウィープセンター(Y座標)
        - w: スウィープサイズ(幅)
        - h: スウィープサイズ(高さ)
        """
        if self._camera:
            return self._camera.sweepSelect(cx, cy, w, h)
        return ()
    
    def clickFeedback(self, cx, cy, target):
        """
        マウスクリックによるフィードバックテスト
        - cx: クリックポイント(X座標)
        - cy: クリックポイント(Y座標)
        - target: フィードバックテスト対象のノードのID
        """
        if self._camera:
            return self._camera.clickFeedback(cx, cy, target)
        return ()
    
    def sweepFeedback(self, cx, cy, w, h, target):
        """
        マウススウィープによるフィードバックテスト
        - cx: クリックポイント(X座標)
        - cy: クリックポイント(Y座標)
        - target: フィードバックテスト対象のノードのID
        - w: スウィープサイズ(幅)
        - h: スウィープサイズ(高さ)
        """
        if self._camera:
            return self._camera.sweepFeedback(cx, cy, w, h, target)
        return ()
    
    def getNodeById(self, id):
        """
        IDによるノード検索
        カメラ配下から、指定されたIDのノードを検索します
        - id: 検索するノードID
        """
        if self._camera:
            return self._camera.getNodeById(id)
        return None
    
    def getNodeByName(self, name):
        """
        名前によるノード検索
        カメラ配下から、指定された名前のノードを検索し、最初に見つかった
        ノードを返します
        - name: 検索するノードの名前
        """
        if self._camera:
            return self._camera.getNodeByName(name)
        return None

    def getViewportMatrix(self):
        """
        ビューポート変換行列を返す
          (-1,-1)-(1,1) --> (ox,oy+height)-(ox+width,oy)
          (minz,maxZ) --> (0,1)
        """
        w = self._viewport[2] * 0.5
        h = self._viewport[3] * 0.5
        minZ = 0.0; maxZ = 1.0
        r = maxZ / (maxZ - minZ)
        
        VPM = Mat4()
        VPM[0] = w
        VPM[5] = -h
        VPM[10] = r
        VPM[12] = w + self._viewport[0]
        VPM[13] = h + self._viewport[1]
        VPM[14] = -r*minZ
        return VPM
    
    def getObjCoord(self, tid, tpos, objCoord):
        """
        オブジェクト座標への変換
        描画領域でのウインドウ座標を、指定したノードのローカル座標系の
        座標値に変換します。成功すればTrueを返します。
        - tid: ターゲットノードのID
        - tpos: ウインドウ座標
        - objCoord: ローカル座標系での座標値の格納領域
        """
        if not self._camera: return False
        if self._viewport[2] < 1 or self._viewport[3] < 1: return False
        asp = float(self._viewport[2])/float(self._viewport[3])
        pM = self._camera.getProjMatrix(asp)
        mM = Mat4()
        if not self._camera.accumMatrix(tid, mM):
            return False
        projMat = N.ndarray((4,4))
        projMat[:][:] = pM.m_v.reshape(4,4)[:][:]
        modelMat = N.ndarray((4,4))
        modelMat[:][:] = mM.m_v.reshape(4,4)[:][:]
        spos = tpos
        winx = float(spos.x)
        winy = float(self._viewport[3] - spos.y)
        winz = 1.0 - self._camera.getFocusDepth()
        (objx, objy, objz) = gluUnProject(winx, winy, winz,
                                          model=modelMat, proj=projMat)
        objCoord[0] = objx
        objCoord[1] = objy
        objCoord[2] = objz
        return True

    def getWinCoord(self, tid, tpos, winCoord):
        """
        ウインドウ座標への変換
        指定したノードのローカル座標系のを、描画領域のウインドウ座標系の
        座標値に変換します。成功すればTrueを返します。
        - tid: ターゲットノードのID
        - tpos: ローカル座標系での座標値
        - winCoord: ウインドウ座標の格納領域
        """
        if not self._camera: return False
        if self._viewport[2] < 1 or self._viewport[3] < 1: return False
        asp = float(self._viewport[2])/float(self._viewport[3])
        pM = self._camera.getProjMatrix(asp)
        mM = Mat4()
        if not self._camera.accumMatrix(tid, mM):
            return False
        projMat = N.ndarray((4,4))
        projMat[:][:] = pM.m_v.reshape(4,4)[:][:]
        modelMat = N.ndarray((4,4))
        modelMat[:][:] = mM.m_v.reshape(4,4)[:][:]
        (objx, objy, objz) = (tpos[0], tpos[1], tpos[2])
        (winx, winy, winz) = gluProject(objx, objy, objz, modelMat, projMat)
        winCoord.x = winx
        winCoord.y = winy
        return True

    def isOnScreen(self, x, y):
        """
        ビューポートテスト
        指定したウインドウ座標がビューポート内にあるかを返します。
        - x: ウインドウ座標値(X座標)
        - y: ウインドウ座標値(Y座標)
        """
        if 0 <= x and x < self._viewport[2] and \
                0 <= y and y < self._viewport[3]:
            return True
        return False

    def startRubberBox(self, p0):
        """
        ラバーボックスの始点を設定する
        - p0: ラバーボックスの始点
        """
        self._rb1.x = self._rb0.x = p0.x
        self._rb1.y = self._rb0.y = p0.y
        self.drawRB(self._rb0, self._rb1)
        return
    
    def drawRubberBox(self, p):
        """
        ラバーボックスを描画する
        - p: ラバーボックスの終点
        """
        self._rb1.x = p.x
        self._rb1.y = p.y
        self.drawRB(self._rb0, self._rb1)
        return
    
    def clearRubberBox(self):
        """
        ラバーボックスを消去する
        """
        self.drawRB(self._rb0, self._rb1)
        return (self._rb0, self._rb1)

    def rotateNode(self, selectedObj, mp, md):
        """
        マウスの位置および移動量に応じて、指定されたノードを回転させる
        - selectedObj ノード
        - mp マウスポインタの位置
        - md マウスポインタの移動量
        """
        if selectedObj == None: return False
        tid = selectedObj._id
        M = selectedObj._matrix
        asp = float(self._viewport[2])/float(self._viewport[3])
        pM = self._camera.getProjMatrix(asp)
        mM = Mat4()
        if not self._camera.accumMatrix(tid, mM): return False
        VP = (C.c_int*4)(); VP[0:4] = self._viewport[0:4]
        xmp = (C.c_int*2)(); xmp[0:2] = [int(mp.x), int(mp.y)]
        xmd = (C.c_int*2)(); xmd[0:2] = [int(md.x), int(md.y)]
        ret = vfr_impl.drawArea_DragRotMatrix(
            M.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            pM.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            mM.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            1.0 - self._camera.getFocusDepth(), VP, xmp, xmd)
        if ret == 0: return False
        selectedObj.setMatrix(M)
        return True

    def translateNode(self, selectedObj, mp, md):
        """
        マウスの位置および移動量に応じて、指定されたノードを平行移動させる
        - selectedObj ノード
        - mp マウスポインタの位置
        - md マウスポインタの移動量
        """
        if selectedObj == None: return False
        tid = selectedObj._id
        M = selectedObj._matrix
        asp = float(self._viewport[2])/float(self._viewport[3])
        pM = self._camera.getProjMatrix(asp)
        mM = Mat4()
        if not self._camera.accumMatrix(tid, mM): return False
        VP = (C.c_int*4)(); VP[0:4] = self._viewport[0:4]
        xmp = (C.c_int*2)(); xmp[0:2] = [int(mp.x), int(mp.y)]
        xmd = (C.c_int*2)(); xmd[0:2] = [int(md.x), int(md.y)]
        ret = vfr_impl.drawArea_DragTransMatrix(
            M.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            pM.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            mM.m_v.ctypes.data_as(C.POINTER(C.c_float)),
            1.0 - self._camera.getFocusDepth(), VP, xmp, xmd)
        if ret == 0: return False
        selectedObj.setMatrix(M)
        return True

    def scaleNode(self, selectedObj, mp, md):
        """
        マウスの位置および移動量に応じて、指定されたノードをスケーリングさせる
        - selectedObj ノード
        - mp マウスポインタの位置
        - md マウスポインタの移動量
        """
        if selectedObj == None: return False
        vpSize = self.getSize()
        if vpSize.y < 1: return False
        if md.y == 0: return False
        if md.y < 0:
            s = -md.y / (vpSize.y * 0.5) + 1.0
        else:
            s = -0.5 * md.y / (vpSize.y * 0.5) + 1.0
        selectedObj.scale(s)
        return True

    def clearDispList(self):
        """
        ディスプレイリストを無効にする
        """
        if self._camera:
            self._camera.clearDispList()
        return
