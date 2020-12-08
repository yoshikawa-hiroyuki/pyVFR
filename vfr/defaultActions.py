# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import wx
import math
from .events import *
from . import camera
from . import scene


#----------------------------------------------------------------------
"""マウスボタンタイプ"""
(VFRDA_MBLEFT, VFRDA_MBRIGHT, VFRDA_MBMIDDLE) = (0x1, 0x1<<1, 0x1<<2)

"""選択ノード"""
_SelectedNode = None


#----------------------------------------------------------------------
class KeyInAction(Action):
    """
    デフォルトキー入力アクションクラス
    drawAreaに対するキー入力処理を行うデフォルトアクションのクラスです．
    デフォルトの動作として，Returnキー入力で選択ノードの幾何変換のリセットを，
    Spaceキー入力でフルスクリーン表示の切り替えを，Escキー入力で
    アプリケーションの終了を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        if not e.isKeyEvent(): return
        da = e.getScreen()
        if da == None: return
        kc = e.getKey()
        if kc == wx.WXK_RETURN:
            if _SelectedNode:
                _SelectedNode.identity()
                _SelectedNode.chkNotice()
            else:
                cam = da.getCamera()
                if cam:
                    cam.identity()
                    cam.chkNotice()
            return
        elif kc == wx.WXK_SPACE:
            frame = da._canvas.GetParent()
            frame.ShowFullScreen(not frame.IsFullScreen(), wx.FULLSCREEN_ALL)
            return
        elif kc == wx.WXK_ESCAPE:
            import sys
            sys.exit(0)

#----------------------------------------------------------------------
class ClickSelectAction(Action):
    """
    デフォルトクリックアクションクラス
    drawAreaに対するマウスクリック処理を行うデフォルトアクションのクラスです．
    デフォルトの動作として，マウスクリック位置でのセレクションテストを実行し，
    ノード選択を行います．
      _bType: マウスボタンタイプ
              ノード選択時のドラッギングイベント切り替えの対象になります
    """
    def __init__(self, bt =VFRDA_MBLEFT):
        Action.__init__(self)
        self._bType = bt
    
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        if not e.isClickEvent(): return
        da = e.getScreen()
        if da == None: return
        cp = e.getMPoint()
        r = da.clickSelect(cp.x, cp.y)
        if _SelectedNode:
            _SelectedNode.setBboxShowMode(False)
            _SelectedNode = None
        if len(r) > 0:
            co = da.getNodeById(r[0])
            if co:
                rr = da.clickFeedback(cp.x, cp.y, r[0])
                co.setBboxShowMode(True)
                _SelectedNode = co
                # Change Actions to xform _SelectedNode
                if self._bType & VFRDA_MBLEFT:
                    da.getEvent(EVT_SDrag).regist(TransNodeAction())
                    da.getEvent(EVT_CDrag).regist(RotNodeAction())
                    da.getEvent(EVT_SCDrag).regist(ScaleNodeAction())
                if self._bType & VFRDA_MBRIGHT:
                    da.getEvent(EVT_RSDrag).regist(TransNodeAction())
                    da.getEvent(EVT_RCDrag).regist(RotNodeAction())
                    da.getEvent(EVT_RSCDrag).regist(ScaleNodeAction())
                if self._bType & VFRDA_MBMIDDLE:
                    da.getEvent(EVT_MSDrag).regist(TransNodeAction())
                    da.getEvent(EVT_MCDrag).regist(RotNodeAction())
                    da.getEvent(EVT_MSCDrag).regist(ScaleNodeAction())
                return
        # Change Actions to xform camera
        if self._bType & VFRDA_MBLEFT:
            da.getEvent(EVT_SDrag).regist(TransCameraAction())
            da.getEvent(EVT_CDrag).regist(RotCameraAction())
            da.getEvent(EVT_SCDrag).regist(ScaleCameraAction())
        if self._bType & VFRDA_MBRIGHT:
            da.getEvent(EVT_RSDrag).regist(TransCameraAction())
            da.getEvent(EVT_RCDrag).regist(RotCameraAction())
            da.getEvent(EVT_RSCDrag).regist(ScaleCameraAction())
        if self._bType & VFRDA_MBMIDDLE:
            da.getEvent(EVT_MSDrag).regist(TransCameraAction())
            da.getEvent(EVT_MCDrag).regist(RotCameraAction())
            da.getEvent(EVT_MSCDrag).regist(ScaleCameraAction())
        return

#----------------------------------------------------------------------
class StartRBoxAction(Action):
    """
    デフォルトドラッグ開始アクションクラス
    drawAreaに対するマウスドラッグ開始処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，バウンディングボックスの描画を開始します．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        da = e.getScreen()
        if da == None: return
        cp = e.getMPoint()
        da.startRubberBox(cp)
        return

#----------------------------------------------------------------------
class EndRBoxAction(Action):
    """
    デフォルトドラッグ終了アクションクラス
    drawAreaに対するマウスドラッグ終了処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，バウンディングボックスを消去し，
    バウンディングボックス領域に対してセレクションテストを実行し，ノード選択を
    行います．
      _bType: マウスボタンタイプ
              ノード選択時のドラッギングイベント切り替えの対象になります
    """
    def __init__(self, bt =VFRDA_MBLEFT):
        Action.__init__(self)
        self._bType = bt
    
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        da = e.getScreen()
        if da == None: return
        (cp0, cp1) = da.clearRubberBox()
        w = cp1.x - cp0.x
        h = cp1.y - cp0.y
        if w < 0:
            cp0.x += w
            w *= -1
        if h < 0:
            cp0.y += h
            h *= -1
        r = da.sweepSelect(cp0.x, cp0.y, w, h)
        if _SelectedNode:
            _SelectedNode.setBboxShowMode(False)
            _SelectedNode = None
        #print 'selection test: #of hits = ', len(r)
        if len(r) > 0:
            co = da.getNodeById(r[0])
            #print '  hits:', r[0:]
            if co:
                rr = da.sweepFeedback(cp0.x, cp0.y, w, h, r[0])
                co.setBboxShowMode(True)
                _SelectedNode = co
                # Change Actions to xform _SelectedNode
                if self._bType & VFRDA_MBLEFT:
                    da.getEvent(EVT_SDrag).regist(TransNodeAction())
                    da.getEvent(EVT_CDrag).regist(RotNodeAction())
                    da.getEvent(EVT_SCDrag).regist(ScaleNodeAction())
                if self._bType & VFRDA_MBRIGHT:
                    da.getEvent(EVT_RSDrag).regist(TransNodeAction())
                    da.getEvent(EVT_RCDrag).regist(RotNodeAction())
                    da.getEvent(EVT_RSCDrag).regist(ScaleNodeAction())
                if self._bType & VFRDA_MBMIDDLE:
                    da.getEvent(EVT_MSDrag).regist(TransNodeAction())
                    da.getEvent(EVT_MCDrag).regist(RotNodeAction())
                    da.getEvent(EVT_MSCDrag).regist(ScaleNodeAction())
                return
        # Change Actions to xform camera
        if self._bType & VFRDA_MBLEFT:
            da.getEvent(EVT_SDrag).regist(TransCameraAction())
            da.getEvent(EVT_CDrag).regist(RotCameraAction())
            da.getEvent(EVT_SCDrag).regist(ScaleCameraAction())
        if self._bType & VFRDA_MBRIGHT:
            da.getEvent(EVT_RSDrag).regist(TransCameraAction())
            da.getEvent(EVT_RCDrag).regist(RotCameraAction())
            da.getEvent(EVT_RSCDrag).regist(ScaleCameraAction())
        if self._bType & VFRDA_MBMIDDLE:
            da.getEvent(EVT_MSDrag).regist(TransCameraAction())
            da.getEvent(EVT_MCDrag).regist(RotCameraAction())
            da.getEvent(EVT_MSCDrag).regist(ScaleCameraAction())
        return

#----------------------------------------------------------------------
class DrawRBoxAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，バウンディングボックスの更新を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        da = e.getScreen()
        if da == None: return
        cp = e.getMPoint()
        da.clearRubberBox()
        da.drawRubberBox(cp)
        return

#----------------------------------------------------------------------
class RotCameraAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，cameraの視界の回転を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        da = e.getScreen()
        if da == None: return
        mv = e.getMMove()
        cam = da.getCamera()
        if cam == None: return
        cam.dragRot(mv.x, mv.y)
        return

#----------------------------------------------------------------------
class TransCameraAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，cameraの視点の平行移動を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        da = e.getScreen()
        if da == None: return
        mv = e.getMMove()
        cam = da.getCamera()
        if cam == None: return
        cam.dragTrans(mv.x, mv.y)
        return

#----------------------------------------------------------------------
class ScaleCameraAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，cameraの視界の拡大縮小(視点の前後移動)を
    行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        da = e.getScreen()
        if da == None: return
        mv = e.getMMove()
        cam = da.getCamera()
        if cam == None: return
        cam.dragTransZ(mv.x, mv.y)
        return

#----------------------------------------------------------------------
class TransNodeAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，選択ノードの平行移動を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        da = e.getScreen()
        if da == None: return
        if _SelectedNode == None: return
        da.translateNode(_SelectedNode, e.getMPoint(), e.getMMove())
        return

#----------------------------------------------------------------------
class RotNodeAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，選択ノードの回転を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        da = e.getScreen()
        if da == None: return
        if _SelectedNode == None: return
        da.rotateNode(_SelectedNode, e.getMPoint(), e.getMMove())
        return

#----------------------------------------------------------------------
class ScaleNodeAction(Action):
    """
    デフォルトドラッギングアクションクラス
    drawAreaに対するマウスドラッギング処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，選択ノードの拡大縮小を行います．
    """
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        global _SelectedNode
        da = e.getScreen()
        if da == None: return
        if _SelectedNode == None: return
        da.scaleNode(_SelectedNode, e.getMPoint(), e.getMMove())
        return

#----------------------------------------------------------------------
class WheelZoomCameraAction(Action):
    """
    デフォルトホイール回転アクションクラス
    drawAreaに対するマウスホイール回転処理を行うデフォルトアクションのクラス
    です．デフォルトの動作として，cameraの視界の拡大縮小(視点の前後移動)を
    行います．
      delta: 回転量に対する前後移動量の比率
    """
    def __init__(self, delta =20):
        self._delta = delta
    
    def execute(self, e):
        """
        仮想イベントに対するリアクション
        - e: 仮想イベント
        """
        da = e.getScreen()
        if da == None: return
        cam = da.getCamera()
        if cam == None: return
        wr = e.getWheelRot()
        if wr > 0:
            mvy = -self._delta
        else:
            mvy = self._delta
        cam.dragTransZ(0, mvy)


#----------------------------------------------------------------------
def SetDefaultAction(da):
    """
    デフォルトアクション群の登録
    指定されたdrawAreaに対し以下のようにデフォルトのアクション設定を行います．
      [仮想イベント]	[アクションクラス]	[動作]
      KeyIn		KeyInAction		Returnで幾何変換をリセット
      						Escで終了
      Click		ClickSelectAction	クリックセレクションテスト
      DragStart		StartRBoxAction		ラバーバンド描画開始
      Drag		DrawRBoxAction		ラバーバンド再描画
      DragEnd		EndRBoxAction		ラバーバンドセレクションテスト
      SClick		None			なし
      SDragStart	None			なし
      SDrag		TransCameraAction	カメラ平行移動
      			TransObjAction		選択ノード平行移動
      SDragEnd		None			なし
      CClick		None			なし
      CDragStart	None			なし
      CDrag		RotCameraAction		カメラ回転
      			RotObjAction		選択ノード回転
      CDragEnd		None			なし
      SCClick		None			なし
      SCDragStart	None			なし
      SCDrag		ScaleCameraAction	カメラ視野拡大縮小
      			ScaleObjAction		選択ノード拡大縮小
      SCDragEnd		None			なし
      MouseWheel	WheelZoomCameraAction	カメラ視野拡大縮小
    - da: アクションを登録するdrawArea
    """
    if da == None: return
    
    # Key Input
    keyin = da.getEvent(EVT_KeyIn)
    keyin.regist(KeyInAction())

    # Click Selection
    click = da.getEvent(EVT_Click)
    click.regist(ClickSelectAction())

    # Dragging : Rubber-Box and Selection
    dragStart = da.getEvent(EVT_DragStart)
    dragStart.regist(StartRBoxAction())

    dragEnd = da.getEvent(EVT_DragEnd)
    dragEnd.regist(EndRBoxAction())

    drag = da.getEvent(EVT_Drag)
    drag.regist(DrawRBoxAction())

    # Shift+Dragging : Camera Translation
    Sdrag = da.getEvent(EVT_SDrag)
    Sdrag.regist(TransCameraAction())

    # Cntl+Dragging : Camera Rotation
    Cdrag = da.getEvent(EVT_CDrag)
    Cdrag.regist(RotCameraAction())

    # Shift+Cntl+Dragging : Camera Scaling
    SCdrag = da.getEvent(EVT_SCDrag)
    SCdrag.regist(ScaleCameraAction())

    # Wheel
    Wheel = da.getEvent(EVT_Wheel)
    Wheel.regist(WheelZoomCameraAction())

    return
