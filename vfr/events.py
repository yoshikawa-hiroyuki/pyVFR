# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .gfxNode import *


#----------------------------------------------------------------------
"""マウスボタン種別"""
(EVT_MB_NONE, EVT_MB_LEFT, EVT_MB_RIGHT, EVT_MB_MIDDLE) = (0, 1<<0, 1<<1, 1<<2)

"""仮想イベントタイプ"""
(EVT_KeyIn,
 EVT_Click,    EVT_DragStart,    EVT_DragEnd,    EVT_Drag,
 EVT_SClick,   EVT_SDragStart,   EVT_SDragEnd,   EVT_SDrag,
 EVT_CClick,   EVT_CDragStart,   EVT_CDragEnd,   EVT_CDrag,
 EVT_SCClick,  EVT_SCDragStart,  EVT_SCDragEnd,  EVT_SCDrag,
 EVT_RClick,   EVT_RDragStart,   EVT_RDragEnd,   EVT_RDrag,
 EVT_RSClick,  EVT_RSDragStart,  EVT_RSDragEnd,  EVT_RSDrag,
 EVT_RCClick,  EVT_RCDragStart,  EVT_RCDragEnd,  EVT_RCDrag,
 EVT_RSCClick, EVT_RSCDragStart, EVT_RSCDragEnd, EVT_RSCDrag,
 EVT_MClick,   EVT_MDragStart,   EVT_MDragEnd,   EVT_MDrag,
 EVT_MSClick,  EVT_MSDragStart,  EVT_MSDragEnd,  EVT_MSDrag,
 EVT_MCClick,  EVT_MCDragStart,  EVT_MCDragEnd,  EVT_MCDrag,
 EVT_MSCClick, EVT_MSCDragStart, EVT_MSCDragEnd, EVT_MSCDrag,
 EVT_Wheel,    EVT_Size,         EVT_Paint) = range(52)


#----------------------------------------------------------------------
class Event(object):
    """
    Eventクラスは，drawAreaに対する仮想イベントの基底クラスです．
      _keyCode: イベント発生時の入力キーコード
      _point: イベント発生時のマウス位置
      _move: イベント発生時のマウス移動量
      _wheelRot: イベント発生時のマウスホイール回転量
      _shifted: Shiftキー押下フラグ
      _controlled: Ctrlキー押下フラグ
      _btnType: マウスボタン種別
                (EVT_MB_NONE/EVT_MB_LEFT/EVT_MB_RIGHT/EVT_MB_MIDDLE)
      _action: アクションへの参照
      _screen: drawAreaへの参照
    """
    def __init__(self, da, mb =EVT_MB_LEFT, shift =False, control =False):
        self._keyCode = 0
        self._point = Point2()
        self._move = Point2()
        self._wheelRot = 0
        self._shifted = shift
        self._controlled = control
        self._btnType = EVT_MB_NONE
        self._action = None
        self._screen = da

    def regist(self, act):
        """
        アクションの登録
        アクション(イベントハンドラ)を登録します．
        Noneを登録すると，ノーリアクションの状態になります．
        - act: アクションへの参照
        """
        self._action = act

    def execAction(self):
        """
        アクションの実行
        登録されているアクションのexecute()をコールします．
        """
        if self._action: self._action.execute(self)

    def getAction(self):
        """
        登録されているアクションを返す．
        """
        return self._action

    def getScreen(self):
        """
        drawAreaへの参照を返す．
        """
        return self._screen
    getDrawArea = getScreen

    def getMPoint(self):
        """
        イベント発生時のマウス位置を返す．
        """
        return self._point

    def setMPoint(self, p):
        """
        イベント発生時のマウス位置を設定する．
        - p: マウス位置
        """
        (self._point.x, self._point.y) = (p.x, p.y)

    def getMMove(self):
        """
        イベント発生時のマウス移動量を返す．
        """
        return self._move

    def setMMove(self, p):
        """
        イベント発生時のマウス移動量を設定する．
        - p: マウス移動量
        """
        (self._move.x, self._move.y) = (p.x, p.y)

    def getKey(self):
        """
        イベント発生時の入力キーコードを返す．
        """
        return self._keyCode

    def setKey(self, kc):
        """
        イベント発生時の入力キーコードを設定する．
        - kc: 入力キーコード
        """
        self._keyCode = kc

    def getWheelRot(self):
        """
        イベント発生時のマウスホイール回転量を返す．
        """
        return self._wheelRot

    def setWheelRot(self, wr):
        """
        イベント発生時のマウスホイール回転量を設定する．
        - wr: ホイール回転量
        """
        self._wheelRot = wr

    def isKeyEvent(self):
        """
        キー入力イベントかどうかを返す．
        """
        return False

    def isClickEvent(self):
        """
        マウスクリックイベントかどうかを返す．
        """
        return False

    def isDragEvent(self):
        """
        マウスドラッギングイベントかどうかを返す．
        """
        return False

    def isDragStartEvent(self):
        """
        マウスドラッグ開始イベントかどうかを返す．
        """
        return False

    def isDragEndEvent(self):
        """
        マウスドラッグ終了イベントかどうかを返す．
        """
        return False

    def isWheelEvent(self):
        """
        マウスホイール回転イベントかどうかを返す．
        """
        return False

    def isSizeEvent(self):
        """
        サイズ変更イベントかどうかを返す．
        """
        return False

    def isPaintEvent(self):
        """
        再描画イベントかどうかを返す．
        """
        return False

    def withLeftButton(self):
        """
        マウス左ボタンイベントかどうかを返す．
        """
        return (self._btnType == EVT_MB_LEFT)

    def withRightButton(self):
        """
        マウス右ボタンイベントかどうかを返す．
        """
        return (self._btnType == EVT_MB_RIGHT)

    def withMiddleButton(self):
        """
        マウス中ボタンイベントかどうかを返す．
        """
        return (self._btnType == EVT_MB_MIDDLE)

    def withShiftKey(self):
        """
        Shiftキー押下イベントかどうかを返す．
        """
        return self._shifted

    def withControlKey(self):
        """
        Ctrlキー押下イベントかどうかを返す．
        """
        return self._controlled


#----------------------------------------------------------------------
class EvKeyIn(Event):
    """
    EvKeyInクラスは，drawAreaに対するKeyIn仮想イベントクラスです．
    """
    def __init__(self, da):
        Event.__init__(self, da)

    def isKeyEvent(self):
        """
        キー入力イベントかどうかを返す．
        """
        return True

    def setKeyShifted(self, ks):
        """
        Shiftキー押下フラグを設定する．
        - ks: Shiftキー押下フラグ
        """
        self._shifted = ks

    def setKeyControlled(self, kc):
        """
        Ctrlキー押下フラグを設定する．
        - kc: Ctrlキー押下フラグ
        """
        self._controlled = kc


#----------------------------------------------------------------------
class EvClick(Event):
    """
    EvClickクラスは，drawAreaに対するClick仮想イベントクラスです．
    """
    def __init__(self, da, mb =EVT_MB_LEFT, shift =False, control =False):
        Event.__init__(self, da, mb, shift, control)

    def isClickEvent(self):
        """
        マウスクリックイベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvDragStart(Event):
    """
    EvDragStartクラスは，drawAreaに対するDragStart仮想イベントクラスです．
    """
    def __init__(self, da, mb =EVT_MB_LEFT, shift =False, control =False):
        Event.__init__(self, da, mb, shift, control)

    def isDragStartEvent(self):
        """
        マウスドラッグ開始イベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvDrag(Event):
    """
    EvDragクラスは，drawAreaに対するDrag仮想イベントクラスです．
    """
    def __init__(self, da, mb =EVT_MB_LEFT, shift =False, control =False):
        Event.__init__(self, da, mb, shift, control)

    def isDragEvent(self):
        """
        マウスドラッギングイベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvDragEnd(Event):
    """
    EvDragEndクラスは，drawAreaに対するDragEnd仮想イベントクラスです．
    """
    def __init__(self, da, mb =EVT_MB_LEFT, shift =False, control =False):
        Event.__init__(self, da, mb, shift, control)

    def isDragEndEvent(self):
        """
        マウスドラッグ終了イベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvWheel(Event):
    """
    EvWheelクラスは，drawAreaに対するWheel仮想イベントクラスです．
    """
    def __init__(self, da, mb =EVT_MB_MIDDLE, shift =False, control =False):
        Event.__init__(self, da, mb, shift, control)

    def isWheelEvent(self):
        """
        マウスホイール回転イベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvSize(Event):
    """
    EvSizeクラスは，drawAreaに対するサイズ変更仮想イベントクラスです．
    """
    def __init__(self, da):
        Event.__init__(self, da)

    def isSizeEvent(self):
        """
        サイズ変更イベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class EvPaint(Event):
    """
    EvPaintクラスは，drawAreaに対する再描画仮想イベントクラスです．
    """
    def __init__(self, da):
        Event.__init__(self, da)

    def isPaintEvent(self):
        """
        再描画イベントかどうかを返す．
        """
        return True


#----------------------------------------------------------------------
class Action(object):
    """
    Actionクラスは，drawAreaに対する仮想イベントのアクション(イベントハンドラ)
    の基底クラスです．
    """
    def execute(self, ev):
        """
        仮想イベントに対するリアクション(派生クラスで実装されます)
        - e: 仮想イベント
        """
        pass
