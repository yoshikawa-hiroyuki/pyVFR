#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sys
import VisObj
import CMap


#----------------------------------------------------------------------
class ObjPropDlg(wx.Dialog):
    """ ObjPropDlgクラス.
    """
    
    def __init__(self, visObj, parent=None):
        """ 初期設定.
        ObjPropダイアログのUIを作成します.
          visObj - VisObj. プロパティを定する対象.
          parent - wx.Window. 親widget
        """
        wx.Dialog.__init__(self, parent, -1, "Set VisObj properties")
        self._visObj = visObj

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # delete
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.deleteBtn = wx.Button(self, label='delete')
        sizerH.Add(self.deleteBtn, flag=wx.ALL, border=3)
        
        # show, lighting, xform
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.showChk = wx.CheckBox(self, label='show')
        sizerH.Add(self.showChk, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        if visObj:
            self.showChk.SetValue(visObj.show)
        self.lightingChk = wx.CheckBox(self, label='lighting')
        sizerH.Add(self.lightingChk, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        if visObj:
            if not visObj.canLighting(): self.lightingChk.Disable()
            else: self.lightingChk.SetValue(visObj.lighting)
            
        self.xformBtn = wx.Button(self, label='xform')
        sizerH.Add(self.xformBtn, flag=wx.ALL, border=3)

        # color, opacity, hilight
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.propBar = CMap.CMapBar(self, size=wx.Size(160,25), showLut=False)
        sizerH.Add(self.propBar, border=3)
        self.propEditBtn = wx.Button(self, label='edit')
        sizerH.Add(self.propEditBtn, flag=wx.ALL, border=3)
        if visObj:
            self.propBar.colour[:] = visObj._colors[0][:]
            self.propBar.hilight = visObj.hilight

        # lut
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.cmapBar = CMap.CMapBar(self, size=wx.Size(160,25))
        sizerH.Add(self.cmapBar, border=3)
        self.cmapEditBtn = wx.Button(self, label='edit')
        sizerH.Add(self.cmapEditBtn, flag=wx.ALL, border=3)

        # lut range
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self, label='min'))
        self.cmapMinTxt = wx.TextCtrl(self, value='0.0', \
                                      style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.cmapMinTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        sizerH.Add(wx.StaticText(self, label='max'))
        self.cmapMaxTxt = wx.TextCtrl(self, value='1.0', \
                                      style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.cmapMaxTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)

        # VisObj param area
        sizerTop.Add(wx.StaticLine(self, size=wx.Size(3,3), \
                                   style=wx.LI_HORIZONTAL), \
                     flag=wx.EXPAND|wx.ALL, border=0)
        
        # VisObj params
        if self._visObj:
            pp = self._visObj.getParamsPanel(self)
            if pp:
                sizerTop.Add(pp, flag=wx.EXPAND|wx.ALL, border=3)

        # sizing
        self.SetSizer(sizerTop)
        sizerTop.Fit(self)
        self.Fit()

        # base event handler setup
        self.Bind(wx.EVT_BUTTON, self.OnDeleteBtn, self.deleteBtn)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowChk, self.showChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnLightingChk, self.lightingChk)
        self.Bind(wx.EVT_BUTTON, self.OnXFormBtn, self.xformBtn)
        self.Bind(wx.EVT_BUTTON, self.OnPropEditBtn, self.propEditBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCMapEditBtn, self.cmapEditBtn)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnCMapMinMaxTxt, self.cmapMinTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnCMapMinMaxTxt, self.cmapMaxTxt)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        
        return

    def __del__(self):
        if self._visObj: del self._visObj
        return
    

    @property
    def visObj(self):
        return self._visObj
    

    # Event handlers
    def OnDeleteBtn(self, event):
        if not self._visObj: return
        self._visObj.destroy()
        return

    def OnShowChk(self, event):
        if not self._visObj: return
        self._visObj.show = self.showChk.GetValue()
        return

    def OnLightingChk(self, event):
        if not self._visObj: return
        if not self.lightingChk: return
        
        return

    def OnXFormBtn(self, event):
        if not self._visObj: return
        self._visObj.showXformDlg(True)
        return
    
    def OnPropEditBtn(self, event):
        if not self._visObj: return
        return

    def OnCMapEditBtn(self, event):
        if not self._visObj: return
        return

    def OnCMapMinMaxTxt(self,event):
        if not self._visObj: return
        return

    def OnDestroy(self, event):
        if self._visObj: self._visObj.destroy()
        return


if __name__ == '__main__':
    app = wx.App()
    dlg = ObjPropDlg(None)
    dlg.Show()
    app.MainLoop()


