#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sys
import xform
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import utilMath


#----------------------------------------------------------------------
class XFormDlg(wx.Dialog):
    """ XFormDlgクラス.
    """
    def __init__(self, xform, parent=None, useC =True, useSz =True):
        """ 初期設定.
        XFormダイアログのUIを作成します.
          xform - object. XFormを設定する対象.
          parent - wx.Window. 親widget
          useC - bool. True:Centerを使用.
          useSz - bool. True:Scaleのz成分を編集可, False:不可. 
        """
        wx.Dialog.__init__(self, parent, -1, "Set XForm")
        self._xform = xform
        
        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # translation
        sizerTop.Add(wx.StaticText(self, label='Translation'))
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self,label='X'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.TxTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.TxTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Y'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.TyTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.TyTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Z'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.TzTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.TzTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)

        # rotation
        sizerTop.Add(wx.StaticText(self, label='Rotation'))
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self,label='X'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.RxTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.RxTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Y'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.RyTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.RyTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Z'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.RzTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.RzTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)

        # scale
        sizerTop.Add(wx.StaticText(self, label='Scale'))
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self,label='X'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.SxTxt = wx.TextCtrl(self, value='1.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.SxTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Y'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.SyTxt = wx.TextCtrl(self, value='1.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.SyTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        sizerH.Add(wx.StaticText(self,label='Z'),
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        self.SzTxt = wx.TextCtrl(self, value='1.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.SzTxt, flag=wx.EXPAND|wx.ALL, proportion=1, border=3)
        if not useSz:
            self.SzTxt.Enable(False)

        # rotation/scale center
        if useC:
            sizerTop.Add(wx.StaticText(self, label='Rot/Scale Center'))
            sizerH = wx.BoxSizer()
            sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
            sizerH.Add(wx.StaticText(self,label='X'),
                       flag=wx.ALIGN_LEFT|wx.ALL, border=3)
            self.CxTxt = wx.TextCtrl(self, value='0.0',
                                     style=wx.TE_PROCESS_ENTER)
            sizerH.Add(self.CxTxt, flag=wx.EXPAND|wx.ALL,
                       proportion=1, border=3)
            sizerH.Add(wx.StaticText(self,label='Y'),
                       flag=wx.ALIGN_LEFT|wx.ALL, border=3)
            self.CyTxt = wx.TextCtrl(self, value='0.0',
                                     style=wx.TE_PROCESS_ENTER)
            sizerH.Add(self.CyTxt, flag=wx.EXPAND|wx.ALL,
                       proportion=1, border=3)
            sizerH.Add(wx.StaticText(self,label='Z'),
                       flag=wx.ALIGN_LEFT|wx.ALL, border=3)
            self.CzTxt = wx.TextCtrl(self, value='0.0',
                                     style=wx.TE_PROCESS_ENTER)
            sizerH.Add(self.CzTxt, flag=wx.EXPAND|wx.ALL,
                       proportion=1, border=3)
        else:
            self.CxTxt = None
            self.CyTxt = None
            self.CzTxt = None

        sizerTop.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)

        # buttons
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL,
                     proportion=1, border=5)
        try:
            sizerH.AddStretchSpacer()
        except AttributeError:
            pass
        self.resetBtn = wx.Button(self, label='Reset')
        sizerH.Add(self.resetBtn, flag=wx.ALL, border=3)
        self.closeBtn = wx.Button(self, label='Close')
        sizerH.Add(self.closeBtn, flag=wx.ALL, border=3)

        self.SetSizer(sizerTop)
        sizerTop.Fit(self)
        self.Fit()

        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.TxTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.TyTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.TzTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.RxTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.RyTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.RzTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.SxTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.SyTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.SzTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.CxTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.CyTxt)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnChangeValues, self.CzTxt)
        self.Bind(wx.EVT_BUTTON, self.OnResetBtn, self.resetBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCloseBtn, self.closeBtn)

        self.update()
        return

    def update(self):
        """ 表示の更新.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not self._xform: return False

        # T
        v = self._xform._T
        self.TxTxt.SetValue(str(v[0]))
        self.TyTxt.SetValue(str(v[1]))
        self.TzTxt.SetValue(str(v[2]))

        # R
        v = self._xform._HPR
        self.RxTxt.SetValue(str(v[1]))
        self.RyTxt.SetValue(str(v[0]))
        self.RzTxt.SetValue(str(v[2]))

        # S
        v = self._xform._S
        self.SxTxt.SetValue(str(v[0]))
        self.SyTxt.SetValue(str(v[1]))
        if self.SzTxt.IsEnabled():
            self.SzTxt.SetValue(str(v[2]))

        # C
        if self.CxTxt:
            v = self._xform._C
            self.CxTxt.SetValue(str(v[0]))
            self.CyTxt.SetValue(str(v[1]))
            self.CzTxt.SetValue(str(v[2]))

        return True

    def updateRefXForm(self):
        """ RefXFormの更新.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not self._xform: return False
        v = utilMath.Vec3()

        # T
        try:
            val = self.TxTxt.GetValue()
            v[0] = float(val)
            val = self.TyTxt.GetValue()
            v[1] = float(val)
            val = self.TzTxt.GetValue()
            v[2] = float(val)
        except (ValueError, TypeError):
            v[0:] = self._xform._T[0:]
            self.TxTxt.SetValue(str(v[0]))
            self.TyTxt.SetValue(str(v[1]))
            self.TzTxt.SetValue(str(v[2]))
        self._xform.setT(v, False)

        # R
        try:
            val = self.RyTxt.GetValue()
            v[0] = float(val)
            val = self.RxTxt.GetValue()
            v[1] = float(val)
            val = self.RzTxt.GetValue()
            v[2] = float(val)
        except (ValueError, TypeError):
            v[0:] = self._xform._HPR[0:]
            self.RxTxt.SetValue(str(v[1]))
            self.RyTxt.SetValue(str(v[0]))
            self.RzTxt.SetValue(str(v[2]))
        self._xform.setHPR(v, False)

        # S
        try:
            val = self.SxTxt.GetValue()
            v[0] = float(val)
            val = self.SyTxt.GetValue()
            v[1] = float(val)
            if self.SzTxt.IsEnabled():
                val = self.SzTxt.GetValue()
                v[2] = float(val)
            else:
                v[2] = 1.0
        except (ValueError, TypeError):
            v[0:] = self._xform._S[0:]
            self.SxTxt.SetValue(str(v[0]))
            self.SyTxt.SetValue(str(v[1]))
            if self.SzTxt.IsEnabled():
                self.SzTxt.SetValue(str(v[2]))
        self._xform.setS(v, False)

        # C
        if self.CxTxt:
            try:
                val = self.CxTxt.GetValue()
                v[0] = float(val)
                val = self.CyTxt.GetValue()
                v[1] = float(val)
                val = self.CzTxt.GetValue()
                v[2] = float(val)
            except (ValueError, TypeError):
                v[0:] = self._xform._C[0:]
                self.CxTxt.SetValue(str(v[0]))
                self.CyTxt.SetValue(str(v[1]))
                self.CzTxt.SetValue(str(v[2]))
        else:
            v[0:3] = [0.0, 0.0, 0.0]
        self._xform.setC(v, False)

        self._xform.updateXForm()
        return True

    # event handlers
    def OnChangeValues(self, evt):
        """ テキスト入力のイベント.
          evt - wx.CommandEvent.
        """
        self.updateRefXForm()

    def OnResetBtn(self, evt):
        """ Resetボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._xform: return False
        self._xform.resetXForm()
        self.update()

    def OnCloseBtn(self, evt):
        """ Closeボタンのイベント.
          evt - wx.CommandEvent.
        """
        if self.IsModal(): self.EndModal(wx.ID_CANCEL)
        else: self.Hide()


if __name__ == '__main__':
    app = wx.App()
    x = xform.XForm()
    dlg = XFormDlg(x)
    #dlg.ShowModal()
    dlg.Show()
    app.Yield()
    import time
    time.sleep(5)
    dlg.SetTitle('AAA')
    app.Yield()
    time.sleep(5)
    print(x)
