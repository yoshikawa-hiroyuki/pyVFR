#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" VisObj
"""
import sys
import wx
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *

import xform, XFormDlg
import CMap


#----------------------------------------------------------------------
class VisObj(gfxGroup.GfxGroup, xform.XForm):
    """ VisObjクラス
    """

    def __init__(self, **args):
        gfxGroup.GfxGroup.__init__(self, **args)
        xform.XForm.__init__(self)

        self.showType = gfxNode.RT_SMOOTH

        self.hilight = 0.0
        self.antiAlias = False
        self.lut = lut.Lut()

        self.xformDlg = None
        self.cmapDlg = None
        self.paramsPnl = None
        
        self.focused = False
        self.setPickMode(gfxNode.PT_OBJECT|gfxNode.PT_BBOX)
        self.setAuxLineColor(False, [1.0, 0.0, 0.0, 0.5])
        self.setBboxColor([1.0, 0.0, 0.0, 0.5])
        self.setBboxWidth(2.5)
        return

    def __del__(self):
        gfxGroup.GfxGroup.__del__(self)

    def destroy(self):
        """ destroy -- override GfxGroup.destroy
        """
        gfxGroup.GfxGroup.destroy(self)
        if not self.xformDlg is None:
            self.xformDlg.Destroy()
            self.xformDlg = None
        if not self.cmapDlg is None:
            self.cmapDlg.Destroy()
            self.cmapDlg = None
        return

    def isVisObj(self):
        """ do not override
        """
        return True

    def isVolObj(self):
        """ override to returns True if Volune rendering VisObj
        """
        return False

    def getVisObjType(self):
        """ override to returns VisObj type string
        """
        return "NoneType"
    

    #---------- "show" property
    @property
    def show(self):
        return (self._renderMode != gfxNode.RT_NONE)

    @show.setter
    def show(self, value):
        if not value:
            self.setRenderMode(gfxNode.RT_NONE)
        else:
            self.setRenderMode(self.showType)
        self.chkNotice()
        return

    #---------- "lighting" property
    @property
    def lighting(self):
        if not self.canLighting():
            return False
        return not (self.showType & gfxNode.RT_NOLIGHT)

    @lighting.setter
    def lighting(self, value):
        if not self.canLighting():
            return
        if value:
            self.showType = self.showType & (not gfxNode.RT_NOLIGHT)
        else:
            self.showType = self.showType & gfxNode.RT_NOLIGHT
        if self.show:
            self.setRenderMode(self.showType)
        return
    
    def canLighting(self):
        if self.showType == gfxNode.RT_POINT or \
           self.showType == gfxNode.RT_WIRE or \
           self.showType == (gfxNode.RT_POINT|gfxNode.RT_WIRE):
            return False
        return True

    
    def setFocus(self, mode):
        """ Focusの設定.
          mode - bool. True:設定, False:解除.
        """
        if self.focused == mode: return
        self.focused = mode
        self.updateRenderMode()
        return

    def updateRenderMode(self):
        self.setBboxShowMode(self.focused)
        return
    
        
    def updateXForm(self):
        """ XFormの更新.
         XFormのmatrixを取得して自身のmatrixに設定します.
        """
        self.setMatrix(self.getXFormMatrix())
        self.chkNotice()
        self.updateUI()
        return

    def showXformDlg(self, show):
        """ Xformダイアログの表示モードの設定.
         show - bool. True:表示, False:非表示
        """
        if self.xformDlg is None:
            if not show: return
            self.xformDlg = XFormDlg.XFormDlg(self, None)
            title = 'XForm: ' + self._name
            self.xformDlg.SetTitle(title)
        self.xformDlg.Show(show)
        return

    def getParamsPanel(self, parent):
        """ パラメータパネルの取得.
        """
        if self.paramsPnl is None:
            self.paramsPnl = wx.Panel(parent)
            self.initPP()
        elif self.paramsPnl.GetParent() != parent:
            self.paramsPnl.Destroy()
            self.paramsPnl = wx.Panel(parent)
            self.initPP()
        self.updatePP()
        return self.paramsPnl

    def initPP(self):
        """ パラメータパネルの初期化(派生クラスで実装).
        """
        return False

    def updatePP(self):
        """ パラメータパネルの値を更新(派生クラスで実装).
        """
        return False

    def updateUI(self):
        """ UIの表示更新.
        """
        if self.xformDlg:
            self.xformDlg.update()
        if self.cmapDlg:
            self.cmapDlg.setLut(self.lut)
        if self.paramsPnl:
            self.updatePP()
        return
    
    def update(self):
        """ 表示更新(派生クラスで実装).
        """
        self.notice()
        return
    
    
