#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" VisObj
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *

import xform, XFormDlg
import CMap


class VisObj(gfxGroup.GfxGroup, xform.XForm):
    """ VisObjクラス
    """

    def __init__(self, name=gfxNode.Node._NONAME, suicide=False):
        gfxGroup.GfxGroup.__init__(self, name, suicide)
        xform.XForm.__init__(self)

        self.hilight = 0.0
        self.antiAlias = False
        self.lut = lut.Lut()

        self.xformDlg = None
        self.cmapDlg = None
        
        self.focused = False
        self.setPickMode(gfxNode.PT_OBJECT|gfxNode.PT_BBOX)
        self.setAuxLineColor(False, [1.0, 0.0, 0.0, 0.5])

    def __del__(self):
        gfxGroup.GfxGroup.__del__(self)

    def destroy(self):
        gfxGroup.GfxGroup.destroy(self)
        if not self.xformDlg is None:
            self.xformDlg.Destroy()
            self.xformDlg = None
        if not self.cmapDlg is None:
            self.cmapDlg.Destroy()
            self.cmapDlg = None
        return

    def isVisObj(self):
        return True

    def isVolObj(self):
        return False

    def setFocus(self, mode):
        """ Focusの設定.
          mode - bool. True:設定, False:解除.
        """
        if self.focused == mode: return
        self.focused = mode
        self.updateRenderMode()
        return

    def updateRenderMode(self):
        pass

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
            self.xformDlg = XFormDlg(self, None)
            title = 'XForm: ' + self._name
            self.xformDlg.SetTitle(title)
        self.xformDlg.Show(show)
        return

    def updateUI(self):
        """ UIの表示更新.
        """
        if self.xformDlg:
            self.xformDlg.update()
        return
    
