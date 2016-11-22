#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from gfxNode import *
from events import *
from drawArea import DrawArea
from sys import platform


"""マウスイベント修飾キータイプ"""
(VFRWX_MEV_SHIFT, VFRWX_MEV_CNTL) = (1<<0, 1<<1)


#----------------------------------------------------------------------
class OglCanvas(glcanvas.GLCanvas):
    """
    OpenGLキャンバスクラス
    wxWidgetsのOpenGL描画用キャンバスをDrawArea用に拡張したクラスです。
      _da: drawAreaへの参照
    """

    def __init__(self, parent, da,
                 pos =wx.DefaultPosition, size =wx.DefaultSize):
        attrLst = (wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER,
                   wx.glcanvas.WX_GL_DEPTH_SIZE, 1)
        glcanvas.GLCanvas.__init__(self, parent=parent, id=-1,
                                   pos=pos, size=size, attribList=attrLst)
        self._da = da
        self.ctx = glcanvas.GLContext(self)

        # events
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMouseMiddleDown)
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMouseMiddleUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)

    def SetCurrentCtx(self):
        self.SetCurrent(self.ctx)

    def OnEraseBackground(self, evt):
        """
        背景クリアのコールバック
        OpenGL描画の際に塗りつぶされるため，何もしません．
        - evt: wxイベント
        """
        pass

    def OnSize(self, evt):
        """
        サイズ変更のコールバック
        - evt: wxイベント
        """
        if self._da:
            self._da.resized()
        evt.Skip()

    def OnPaint(self, evt):
        """
        再描画のコールバック
        - evt: wxイベント
        """
        dc = wx.PaintDC(self)
        self.SetCurrentCtx()
        if self._da:
            self._da.redraw()
        self.SwapBuffers() # may call glFlush()

    def OnMouseLeftDown(self, evt):
        """
        マウス左ボタンダウンのコールバック
        - evt: wxイベント
        """
        self.CaptureMouse()
        if self._da:
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnLButtonDown(mp)

    def OnMouseLeftUp(self, evt):
        """
        マウス左ボタンアップのコールバック
        - evt: wxイベント
        """
        try:
            self.ReleaseMouse()
        except:
            pass
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown(): nFlag |= VFRWX_MEV_CNTL
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnLButtonUp(nFlag, mp)

    def OnMouseMiddleDown(self, evt):
        """
        マウス中ボタンダウンのコールバック
        - evt: wxイベント
        """
        self.CaptureMouse()
        if self._da:
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnMButtonDown(mp)

    def OnMouseMiddleUp(self, evt):
        """
        マウス中ボタンアップのコールバック
        - evt: wxイベント
        """
        try:
            self.ReleaseMouse()
        except:
            pass
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown(): nFlag |= VFRWX_MEV_CNTL
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnMButtonUp(nFlag, mp)
        
    def OnMouseRightDown(self, evt):
        """
        マウス右ボタンダウンのコールバック
        - evt: wxイベント
        """
        self.CaptureMouse()
        if self._da:
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnRButtonDown(mp)

    def OnMouseRightUp(self, evt):
        """
        マウス右ボタンアップのコールバック
        - evt: wxイベント
        """
        try:
            self.ReleaseMouse()
        except:
            pass
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown(): nFlag |= VFRWX_MEV_CNTL
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnRButtonUp(nFlag, mp)

    def OnMouseMotion(self, evt):
        """
        マウス移動のコールバック
        - evt: wxイベント
        """
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown(): nFlag |= VFRWX_MEV_CNTL
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnMouseMove(nFlag, mp)

    def OnKeyDown(self, evt):
        """
        キー入力のコールバック
        - evt: wxイベント
        """
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown():  nFlag |= VFRWX_MEV_CNTL
            kc = evt.GetKeyCode()
            self._da.OnKeyDown(nFlag, kc)

    def OnWheel(self, evt):
        """
        マウスホイール回転のコールバック
        - evt: wxイベント
        """
        if self._da:
            nFlag = 0
            if evt.ShiftDown(): nFlag |= VFRWX_MEV_SHIFT
            if evt.ControlDown(): nFlag |= VFRWX_MEV_CNTL
            wr = evt.GetWheelRotation()
            mp = Point2(evt.GetX(), evt.GetY())
            self._da.OnWheel(nFlag, wr, mp)


#----------------------------------------------------------------------
class DrawAreaWx(DrawArea):
    """
    wxWidgets用描画領域クラス
    wxWidgets用のDrawAreaクラスの実装です。
    内部にOglCanvasクラスを持ち、OpenGLによる描画を実現します。
      _noticeFlag: 描画内容変更フラグ
      _modeState: 仮想イベント状態
      _canvas: OpenGL描画キャンバスへの参照
      _m0: 仮想イベント状態変更前のマウス位置
      _m1: 仮想イベント状態変更後のマウス位置
    """
    def __init__(self, parent, pos =wx.DefaultPosition, size =wx.DefaultSize):
        DrawArea.__init__(self)
        self._noticeFlag = False
        self._modeState = DrawArea.WaitAny
        self._canvas = OglCanvas(parent, self, pos, size)
        self._m0 = Point2()
        self._m1 = Point2()
        return

    def __del__(self):
        del self._canvas

    
    def redraw(self):
        """
        再描画を行う
        OpenGLによるシーングラフ描画とラバーバンドの描画を行います．
        _canvas.OnPaint()より呼び出されます．
        """
        DrawArea.redraw(self)

        #======== Canvas ========
        if self._canvas == None: return

        #======== Rendering ========
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self._camera:
            glEnable(GL_SCISSOR_TEST)
            glViewport(self._viewport[0], self._viewport[1],
                       self._viewport[2], self._viewport[3])
            glScissor(self._viewport[0], self._viewport[1],
                      self._viewport[2], self._viewport[3])
            if self._viewport[3] < 1:
                self._camera.redraw()
            else:
                asp = float(self._viewport[2]) / float(self._viewport[3])
                self._camera.redraw(asp)
            glDisable(GL_SCISSOR_TEST)

        #======== Rubber Box ========
        self.rb_draw()

        #======== Post rendering ========
        # glGetError not ported to PyOpenGL, raise exception.

        self._noticeFlag = False
        return

    def notice(self, invalidateDL =True):
        """
        描画内容の変更通知を行う
        描画内容変更フラグをTrueに設定します．
        """
        self._noticeFlag = True

    def chkNotice(self):
        """
        描画内容の変更検査を行う
        描画内容変更フラグがTrueの場合は_canvasを再描画しフラグをクリアします．
        """
        if self._noticeFlag:
            if self._canvas:
                self._canvas.Refresh(False)
        return
        
    def rumor(self):
        """
        カメラからの破壊通知を受付ける
        カメラからの破壊通知を受け，カメラへの参照をクリアします．
        """
        self._camera = None
    
    def getSize(self):
        """
        描画領域のサイズ(pixels)を返す
        _canvasのサイズを返します．
        """
        size = Point2()
        if self._canvas:
            wsz = self._canvas.GetSize()
            size.x = wsz.x
            size.y = wsz.y
        return size

    def drawImmediate(self):
        """
        イミディアットモードでの描画
        イミディアットモード(OpenGLディスプレイリストを使用しない)で再描画を
        行います．
        """
        bkIM = IsImmediateMode()
        if not bkIM: SetImmediateMode(True)
        self.redraw()
        if not bkIM: SetImmediateMode(False)
        return

    # callbacks
    def OnKeyDown(self, nFlags, nChar):
        """
        キー入力のコールバック
        - nFlag: 修飾キーフラグ
        - nChar: 入力キーコード
        """
        self._canvas.SetCurrentCtx()
        event = self.getEvent(EVT_KeyIn)
        event.setKey(nChar)
        event.setKeyShifted(nFlags & VFRWX_MEV_SHIFT)
        event.setKeyControlled(nFlags & VFRWX_MEV_CNTL)
        event.execAction()
        self.chkNotice()
        return

    def OnWheel(self, nFlags, wheelRot, point):
        """
        マウスホイール回転のコールバック
        - nFlag: 修飾キーフラグ
        - wheelRot: ホイール回転量
        - point: マウス位置
        """
        # don't change self._modeState ...
        self._canvas.SetCurrentCtx()
        event = self.getEvent(EVT_Wheel)
        event._wheelRot = wheelRot
        event._point.x = point.x
        event._point.y = point.y
        event._shifted = (nFlags & VFRWX_MEV_SHIFT)
        event._controlled = (nFlags & VFRWX_MEV_CNTL)
        event.execAction()
        self.chkNotice()
        return
        
    def OnLButtonDown(self, point):
        """
        マウス左ボタンダウンのコールバック
        - point: マウス位置
        """
        self._m0.x = self._m1.x = point.x
        self._m0.y = self._m1.y = point.y
        self._modeState = DrawArea.LBPressed
        return
        
    def OnRButtonDown(self, point):
        """
        マウス右ボタンダウンのコールバック
        - point: マウス位置
        """
        self._m0.x = self._m1.x = point.x
        self._m0.y = self._m1.y = point.y
        self._modeState = DrawArea.RBPressed
        return
    
    def OnMButtonDown(self, point):
        """
        マウス中ボタンダウンのコールバック
        - point: マウス位置
        """
        self._m0.x = self._m1.x = point.x
        self._m0.y = self._m1.y = point.y
        self._modeState = DrawArea.MBPressed
        return

    def OnLButtonUp(self, nFlags, point):
        """
        マウス左ボタンアップのコールバック
        - nFlags: 修飾キーフラグ
        - point: マウス位置
        """
        self._canvas.SetCurrentCtx()
        mv = Point2()
        cs = self.getSize()
        if self._modeState == DrawArea.LBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # SCClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_SCClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # SClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_SClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # CClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_CClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            else:
                # Click
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_Click)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState ==DrawArea. LDraggingSolo:
            # DragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_DragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.LDraggingShift:
            # SDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_SDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.LDraggingCntl:
            # CDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_CDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.LDraggingShiftCntl:
            # SCDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_SCDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        else:
            self._modeState = DrawArea.WaitAny
        self.chkNotice()
        return
                
    def OnRButtonUp(self, nFlags, point):
        """
        マウス右ボタンアップのコールバック
        - nFlags: 修飾キーフラグ
        - point: マウス位置
        """
        self._canvas.SetCurrentCtx()
        mv = Point2()
        cs = self.getSize()
        if self._modeState == DrawArea.RBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # RSCClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RSCClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # RSClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RSClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # RCClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RCClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            else:
                # RClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.RDraggingSolo:
            # RDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_RDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.RDraggingShift:
            # RSDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_RSDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.RDraggingCntl:
            # RCDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_RCDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.RDraggingShiftCntl:
            # RSCDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_RSCDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        else:
            self._modeState = DrawArea.WaitAny
        self.chkNotice()
        return

    def OnMButtonUp(self, nFlags, point):
        """
        マウス中ボタンアップのコールバック
        - nFlags: 修飾キーフラグ
        - point: マウス位置
        """
        self._canvas.SetCurrentCtx()
        mv = Point2()
        cs = self.getSize()
        if self._modeState == DrawArea.MBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # MSCClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MSCClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # MSClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MSClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # MCClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MCClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
            else:
                # MClick
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MClick)
                event.setMPoint(point)
                mv.x = mv.y = 0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.MDraggingSolo:
            # MDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_MDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.MDraggingShift:
            # MSDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_MSDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.MDraggingCntl:
            # MCDragEnd
            self._modeState = DrawArea.WaitAny
            event = self.getEvent(EVT_MCDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.MDraggingShiftCntl:
            # MSCDragEnd
            self._modeState = WaitAny
            event = self.getEvent(EVT_MSCDragEnd)
            self._m1 = event._point = point
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        else:
            self._modeState = DrawArea.WaitAny
        self.chkNotice()
        return
        
    def OnMouseMove(self, nFlags, point):
        """
        マウス移動のコールバック
        - nFlags: 修飾キーフラグ
        - point: マウス位置
        """
        self._canvas.SetCurrentCtx()
        mv = Point2()
        if self._modeState == DrawArea.WaitAny:
            pass
        #---------------------- LeftButton ----------------------
        elif self._modeState == DrawArea.LBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # SCDragStart
                self._modeState = DrawArea.LDraggingShiftCntl
                self._m1 = point
                event = self.getEvent(EVT_SCDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # SDragStart
                self._modeState = DrawArea.LDraggingShift
                self._m1 = point
                event = self.getEvent(EVT_SDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # CDragStart
                self._modeState = DrawArea.LDraggingCntl
                self._m1 = point
                event = self.getEvent(EVT_CDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # DragStart
                self._modeState = DrawArea.LDraggingSolo
                self._m1 = point
                event = self.getEvent(EVT_DragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.LDraggingSolo:
            self._m0 = self._m1
            self._m1 = point
            # Drag
            event = self.getEvent(EVT_Drag)
            event.setMPoint(point)
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.LDraggingShift:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT:
                # SDrag
                event = self.getEvent(EVT_SDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # SDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_SDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.LDraggingCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_CNTL:
                # CDrag
                event = self.getEvent(EVT_CDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # CDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_CDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.LDraggingShiftCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # SCDrag
                event = self.getEvent(EVT_SCDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # SCDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_SCDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        #---------------------- RightButton ----------------------
        elif self._modeState == DrawArea.RBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # RSCDragStart
                self._modeState = DrawArea.RDraggingShiftCntl
                self._m1 = point
                event = self.getEvent(EVT_RSCDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # RSDragStart
                self._modeState = DrawArea.RDraggingShift
                self._m1 = point
                event = self.getEvent(EVT_RSDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # RCDragStart
                self._modeState = DrawArea.RDraggingCntl
                self._m1 = point
                event = self.getEvent(EVT_RCDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # RDragStart
                self._modeState = DrawArea.RDraggingSolo
                self._m1 = point
                event = self.getEvent(EVT_RDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.RDraggingSolo:
            self._m0 = self._m1
            self._m1 = point
            # RDrag
            event = self.getEvent(EVT_RDrag)
            event.setMPoint(point)
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.RDraggingShift:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT:
                # RSDrag
                event = self.getEvent(EVT_RSDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # RSDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RSDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.RDraggingCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_CNTL:
                # RCDrag
                event = self.getEvent(EVT_RCDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # RCDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RCDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.RDraggingShiftCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # RSCDrag
                event = self.getEvent(EVT_RSCDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # RSCDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_RSCDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        #---------------------- MiddleButton ----------------------
        elif self._modeState == DrawArea.MBPressed:
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # MSCDragStart
                self._modeState = DrawArea.MDraggingShiftCntl
                self._m1 = point
                event = self.getEvent(EVT_MSCDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_SHIFT:
                # MSDragStart
                self._modeState = DrawArea.MDraggingShift
                self._m1 = point
                event = self.getEvent(EVT_MSDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            elif nFlags & VFRWX_MEV_CNTL:
                # MCDragStart
                self._modeState = DrawArea.MDraggingCntl
                self._m1 = point
                event = self.getEvent(EVT_MCDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # MDragStart
                self._modeState = DrawArea.MDraggingSolo
                self._m1 = point
                event = self.getEvent(EVT_MDragStart)
                event.setMPoint(self._m0)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.MDraggingSolo:
            self._m0 = self._m1
            self._m1 = point
            # MDrag
            event = self.getEvent(EVT_MDrag)
            event.setMPoint(point)
            mv = self._m1 - self._m0
            event.setMMove(mv)
            event.execAction()
        elif self._modeState == DrawArea.MDraggingShift:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT:
                # MSDrag
                event = self.getEvent(EVT_MSDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # MSDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MSDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.MDraggingCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_CNTL:
                # MCDrag
                event = self.getEvent(EVT_MCDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # MCDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MCDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
        elif self._modeState == DrawArea.MDraggingShiftCntl:
            self._m0 = self._m1
            self._m1 = point
            if nFlags & VFRWX_MEV_SHIFT and nFlags & VFRWX_MEV_CNTL:
                # MSCDrag
                event = self.getEvent(EVT_MSCDrag)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()
            else:
                # MSCDragEnd
                self._modeState = DrawArea.WaitAny
                event = self.getEvent(EVT_MSCDragEnd)
                event.setMPoint(point)
                mv = self._m1 - self._m0
                event.setMMove(mv)
                event.execAction()

        self.chkNotice()
        return
