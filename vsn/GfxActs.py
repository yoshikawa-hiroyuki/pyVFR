#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
""" GfxActs.
  GfxAct_Baseクラス, GfxAct_KeyInクラス, GfxAct_Clickクラス,
  GfxAct_RotSceneクラス, GfxAct_ScaleSceneクラス, GfxAct_TransSceneクラス,
  GfxAct_WheelSceneクラス, GfxAct_StartRBoxクラス, GfxAct_Selectionクラス,
  GfxAct_SweepZoomクラスを提供します.
"""

import wx
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *
from GfxView import GfxView


#----------------------------------------------------------------------
class GfxAct_Base(events.Action):
    """ GfxAct_Baseクラス
     GfxAct_KeyIn, GfxAct_Click, GfxAct_RotScene, GfxAct_ScaleScene,
     GfxAct_TransScene, GfxAct_WheelScene, GfxAct_StartRBox,
     GfxAct_Selection, GfxAct_SweepZoomの基底クラスです.
    """
    def __init__(self, gv):
        """ 初期設定.
          gv - GfxView
        """
        events.Action.__init__(self)
        self.gfxView = gv


#----------------------------------------------------------------------
class GfxAct_KeyIn(GfxAct_Base):
    """ GfxAct_KeyInクラス
    """
    def execute(self, e):
        """ GfxView上のキー操作へのイベントを実行.
          e - event
        """
        if not e.isKeyEvent(): return
        da = e.getScreen()
        if da == None: return
        kc = e.getKey()
        arrDelta = 0.5 # 90 deg.
        if e._controlled: arrDelta = 0.25 # 45 deg.
        elif e._shifted: arrDelta = 1.0 # 180 deg.
        
        vp0 = self.gfxView.getViewPoint() # current view point
        l_viewport = da._viewport[2]
        if l_viewport < da._viewport[3]: l_viewport = da._viewport[3]

        if kc == wx.WXK_ESCAPE:
            # unselect object
            return
        elif kc == wx.WXK_SPACE:
            pTgt = None
            if not e._shifted:
                pass # pTgt is selected object
            self.gfxView.normalize(pTgt)
        elif kc == wx.WXK_LEFT:
            da.rotateNode(self.gfxView._R, gfxNode.Point2(),
                          gfxNode.Point2(-l_viewport*arrDelta, 0))
        elif kc == wx.WXK_RIGHT:
            da.rotateNode(self.gfxView._R, gfxNode.Point2(),
                          gfxNode.Point2(l_viewport*arrDelta, 0))
        elif kc == wx.WXK_UP:
            da.rotateNode(self.gfxView._R, gfxNode.Point2(),
                          gfxNode.Point2(0, -l_viewport*arrDelta))
        elif kc == wx.WXK_DOWN:
            da.rotateNode(self.gfxView._R, gfxNode.Point2(),
                          gfxNode.Point2(0, l_viewport*arrDelta))
        elif kc == wx.WXK_HOME:
            self.gfxView._R.identity()
        elif kc == ord('z') or kc == ord('Z'):
            if e._shifted:
                self.gfxView._S.scale(GfxView.s_keyZoomInRatio2)
            else:
                self.gfxView._S.scale(GfxView.s_keyZoomInRatio)
        elif kc == ord('x') or kc == ord('X'):
            if e._shifted:
                self.gfxView._S.scale(GfxView.s_keyZoomOutRatio2)
            else:
                self.gfxView._S.scale(GfxView.s_keyZoomOutRatio)
        elif kc == ord('c') or kc == ord('C'):
            cp0 = gfxNode.Point2()
            cp1 = gfxNode.Point2(da._viewport[2], da._viewport[3])
            self.gfxView.sweepZoom(cp0, cp1)
        else:
            return

        # do xform animation
        if GfxView.s_xformAnim and \
           GfxView.s_xformAnimDuration > 0.0:
            vp1 = self.gfxView.getViewPoint()
            self.gfxView.setViewPoint(vp0)
            self.gfxView.setViewXForm(vp1)
        self.gfxView.sceneGraphUpdated()
        return


#----------------------------------------------------------------------
class GfxAct_Click(GfxAct_Base):
    """ GfxAct_Clickクラス
    """
    def execute(self, e):
        """ GfxView上のフォーカスのイベントを設定.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        return


#----------------------------------------------------------------------
class GfxAct_RotScene(GfxAct_Base):
    """ GfxAct_RotSceneクラス
    """
    def execute(self, e):
        """ GfxView上の回転のイベントを設定.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        if e.isDragStartEvent():
            self.gfxView.setXforming(True)
        elif e.isDragEndEvent():
            self.gfxView.setXforming(False)
            self.gfxView.sceneGraphUpdated()
        else:
            da.rotateNode(self.gfxView._R, e.getMPoint(), e.getMMove())
            self.gfxView.sceneGraphUpdated()
        return


#----------------------------------------------------------------------
class GfxAct_ScaleScene(GfxAct_Base):
    """ GfxAct_ScaleSceneクラス
    """
    def execute(self, e):
        """ GfxView上の拡大縮小のイベントを設定.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        if e.isDragStartEvent():
            self.gfxView.setXforming(True)
        elif e.isDragEndEvent():
            self.gfxView.setXforming(False)
            self.gfxView.sceneGraphUpdated()
        else:
            da.scaleNode(self.gfxView._S, e.getMPoint(), e.getMMove())
            self.gfxView.sceneGraphUpdated()
        return


#----------------------------------------------------------------------
class GfxAct_TransScene(GfxAct_Base):
    """ GfxAct_TransSceneクラス
    """
    def execute(self, e):
        """ GfxView上の平行移動のイベントを設定.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        if e.isDragStartEvent():
            self.gfxView.setXforming(True)
        elif e.isDragEndEvent():
            self.gfxView.setXforming(False)
            self.gfxView.sceneGraphUpdated()
        else:
            da.translateNode(self.gfxView._T, e.getMPoint(), e.getMMove())
            self.gfxView.sceneGraphUpdated()
        return


#----------------------------------------------------------------------
class GfxAct_WheelScene(GfxAct_Base):
    """ GfxAct_WheelSceneクラス
    """
    def __init__(self, gv, delta =20):
        """ 初期設定.
          gv - GfxView
          delta - delta値
        """
        GfxAct_Base.__init__(self, gv)
        self._delta = delta

    def execute(self, e):
        """ GfxView上のホイール操作へのイベントを設定.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        wr = e.getWheelRot()
        if wr > 0:
            mvy = -self._delta
        else:
            mvy = self._delta
        da.scaleNode(self.gfxView._S, e.getMPoint(), gfxNode.Point2(0, mvy))
        self.gfxView.sceneGraphUpdated()
        return


#----------------------------------------------------------------------
class GfxAct_StartRBox(GfxAct_Base):
    """ GfxAct_StartRBoxクラス
    """
    def __init__(self, gv, lineWidth =2.0, lineType =gfxNode.ST_SOLID,
                 lineColor =[0.8, 0.8, 0.8]):
        """ 初期設定.
          gv - GfxView
          lineWidth - float. ライン幅.
          lineType - int. 線種.
          lineColor - list(float*3). ライン色.
        """
        GfxAct_Base.__init__(self, gv)
        self.lineWidth = lineWidth
        self.lineType = lineType
        self.lineColor = [0.8, 0.8, 0.8, 1.0]
        self.lineColor[0:3] = lineColor[0:3]
        return
    
    def execute(self, e):
        """ GfxView上でRubberBox描画のイベントを実行.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        self.gfxView.setXforming(True)
        da.setRubberBoxColor(self.lineColor)
        da.setRubberBoxLineWidth(self.lineWidth)
        da.setRubberBoxLineType(self.lineType)
        da.startRubberBox(e.getMPoint())
        return


#----------------------------------------------------------------------
class GfxAct_Selection(GfxAct_Base):
    """ GfxAct_Selectionクラス
    """
    def execute(self, e):
        """ GfxView上でNode選択のイベントを実行.
          e - event
        """
        da = e.getScreen()
        if da == None: return
        da._canvas.SetFocus()
        if e.isClickEvent():
            cp = e.getMPoint()
            r = da.clickSelect(cp.x, cp.y)
            if len(r) > 1:
                r = (r[0],)
        elif e.isDragEndEvent():
            (cp0, cp1) = da.clearRubberBox()
            self.gfxView.setXforming(False)
            w = cp1.x - cp0.x
            h = cp1.y - cp0.y
            if w < 0:
                cp0.x += w
                w *= -1
            if h < 0:
                cp0.y += h
                h *= -1
            r = da.sweepSelect(cp0.x, cp0.y, w, h)
        else:
            return

        arena = self.gfxView.parent.arena
        if not arena: return

        nodeLst = ()
        for id in r:
            node = arena.getNodeById(id)
            if not node: continue
            if node in nodeLst: continue
            nodeLst += (node,)
        # select object
        return
    

#----------------------------------------------------------------------
class GfxAct_SweepZoom(GfxAct_Base):
    """ GfxAct_SweepZoomクラス
    """
    def execute(self, e):
        """ GfxView上でsweep zoomのイベントを実行.
          e - event
        """
        # escape from Xforming mode
        self.gfxView.setXforming(False)

        da = e.getScreen()
        if da == None: return
        (cp0, cp1) = da.clearRubberBox()

        vp0 = self.gfxView.getViewPoint() # current view point
        self.gfxView.sweepZoom(cp0, cp1)

        # do xform animation
        if GfxView.s_xformAnim and \
           GfxView.s_xformAnimDuration > 0.0:
            vp1 = self.gfxView.getViewPoint()
            self.gfxView.setViewPoint(vp0)
            self.gfxView.setViewXForm(vp1)

        self.gfxView.sceneGraphUpdated()        
        return
    
