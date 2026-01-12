#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sys
import VisObj
import ObjSelectDlg


#----------------------------------------------------------------------
class EditPropDlg(wx.Dialog):
    """ EditPropDlgクラス.
    """
    
    def __init__(self, parent, visObj=None):
        """ 初期設定.
        EditPropダイアログのUIを作成します.
          parent - wx.Window. 親widget
          visObj - VisObj. プロパティを定する対象.
        """
        wx.Dialog.__init__(self, parent, -1, "Edit VisObj properties")
        self._visObj = visObj
        self.parent = parent

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # top buttons
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.resetBtn = wx.Button(self, label='reset')
        sizerH.Add(self.resetBtn, flag=wx.ALL, border=3)
        self.copyBtn = wx.Button(self, label='copy')
        sizerH.Add(self.copyBtn, flag=wx.ALL, border=3)
        self.colorBtn = wx.Button(self, label='edit base color')
        sizerH.Add(self.colorBtn, flag=wx.ALL, border=3)

        # opacity
        sizerTop.Add(wx.StaticText(self, label='opacity'),
                     flag=wx.ALL, border=2)
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.opacSlider = wx.Slider(self, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        sizerH.Add(self.opacSlider, flag=wx.EXPAND|wx.ALL,
                   proportion=1, border=3)
        self.opacTxt = wx.TextCtrl(self, value='0.0', style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.opacTxt, flag=wx.ALL, border=3)

        # hilight
        sizerTop.Add(wx.StaticText(self, label='hilight'),
                     flag=wx.ALL, border=2)        
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        self.hilightSlider = wx.Slider(self,
                                       style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        sizerH.Add(self.hilightSlider, flag=wx.EXPAND|wx.ALL,
                   proportion=1, border=3)
        self.hilightTxt = wx.TextCtrl(self, value='0.0',
                                      style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.hilightTxt, flag=wx.ALL, border=3)

        # horizontal line
        sizerTop.Add(wx.StaticLine(self, size=wx.Size(3,3), \
                                   style=wx.LI_HORIZONTAL), \
                     flag=wx.EXPAND|wx.ALL, border=0)

        # bottom buttons
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        try:
            sizerH.AddStretchSpacer()
        except AttributeError:
            pass
        self.cancelBtn = wx.Button(self, label='Cancel')
        sizerH.Add(self.cancelBtn, flag=wx.ALL, border=3)
        self.closeBtn = wx.Button(self, label='OK')
        sizerH.Add(self.closeBtn, flag=wx.ALL, border=3)

        # layouts
        self.SetSizer(sizerTop)
        sizerTop.Fit(self)
        self.Fit()

        # event handlers
        self.Bind(wx.EVT_BUTTON, self.OnResetBtn, self.resetBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCopyBtn, self.copyBtn)
        self.Bind(wx.EVT_BUTTON, self.OnColorBtn, self.colorBtn)
        self.Bind(wx.EVT_SLIDER, self.OnOpacSlider, self.opacSlider)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnOpacTxt, self.opacTxt)
        self.Bind(wx.EVT_SLIDER, self.OnHilightSlider, self.hilightSlider)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnHilightTxt, self.hilightTxt)
        self.Bind(wx.EVT_BUTTON, self.OnCancelBtn, self.cancelBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCloseBtn, self.closeBtn)

        # backup for reset
        self.bkupColor = [1.0, 1.0, 1.0, 1.0]
        self.bkupHilight = 0.0
        if self._visObj:
            self.bkupColor[:] = self._visObj._colors[0][:]
            self.bkupHilight = self._visObj.hilight
        
        self.update()
        return

    def update(self):
        """ 表示の更新.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not self._visObj: return False

        # opacity
        opacity = self._visObj._colors[0][3]
        opacInt = int(opacity * 100)
        if opacInt < 0: opacInt = 0
        elif opacInt > 100: opacInt = 100
        self.opacSlider.SetValue(opacInt)
        self.opacTxt.SetValue(str(opacInt))

        # hilight
        hilight = self._visObj.hilight
        hilightInt = int(hilight * 100)
        if hilightInt < 0: hilightInt = 0
        elif hilightInt > 100: hilightInt = 100
        self.hilightSlider.SetValue(hilightInt)
        self.hilightTxt.SetValue(str(hilightInt))

        return True

    def isViewFrame(self):
        return False

    def OnResetBtn(self, evt):
        """ resetボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        # opacity
        self._visObj._colors[0][3] = 1.0

        # hilight
        self._visObj.hilight = 0.0

        # update
        self.update()
        self._visObj.notice()
        self._visObj.chkNotice()
        return

    def OnCopyBtn(self, evt):
        """ copyボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        dlg = ObjSelectDlg.ObjSelectDlg(self, exceptId=self._visObj.getID())
        if dlg.ShowModal() != wx.ID_OK:
            return

        obj = dlg.getSelectedObj()
        if not obj:
            return

        self._visObj._colors[0][3] = obj._colors[0][3]
        self._visObj.hilight = obj.hilight

        self.update()
        self._visObj.notice()
        self._visObj.chkNotice()
        return

    def OnColorBtn(self, evt):
        """ edit base colorボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        colData = wx.ColourData()
        color = self._visObj._colors[0][0:3]
        colData.SetColour(wx.Colour(int(color[0]*255),
                                    int(color[1]*255), int(color[2]*255)))
        dlg = wx.ColourDialog(self, colData)
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        colData = dlg.GetColourData()
        c = colData.GetColour()
        color = [c.Red()/255.0, c.Green()/255.0, c.Blue()/255.0]
        self._visObj._colors[0][0:3] = color[:]
        self._visObj.notice()
        
        self._visObj.chkNotice()
        return

    def OnOpacSlider(self, evt):
        """ opacityスライダーのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        val = self.opacSlider.GetValue()
        self.opacTxt.SetValue(str(val))
        
        opac = float(val/100.0)
        self._visObj._colors[0][3] = opac
        self._visObj.notice()
        
        self._visObj.chkNotice()
        return

    def OnOpacTxt(self, evt):
        """ opacityテキストのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        valStr = self.opacTxt.GetValue()
        try:
            val = int(valStr)
        except:
            self.update()
            return
        if val < 0 or val > 100:
            self.update()
            return
        self.opacSlider.SetValue(val)

        opac = float(val/100.0)
        self._visObj._colors[0][3] = opac
        self._visObj.notice()
        
        self._visObj.chkNotice()
        return

    def OnHilightSlider(self, evt):
        """ hilightスライダーのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        val = self.hilightSlider.GetValue()
        self.hilightTxt.SetValue(str(val))

        hilight = float(val/100.0)
        self._visObj.hilight = hilight
        self._visObj.notice()
        
        self._visObj.chkNotice()
        return

    def OnHilightTxt(self, evt):
        """ hilightテキストのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        valStr = self.hilightTxt.GetValue()
        try:
            val = int(valStr)
        except:
            self.update()
            return
        if val < 0 or val > 100:
            self.update()
            return
        self.hilightSlider.SetValue(val)

        hilight = float(val/100.0)
        self._visObj.hilight = hilight
        self._visObj.notice()
        
        self._visObj.chkNotice()
        return

    def OnCancelBtn(self, evt):
        """ Cancelボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return

        self._visObj._colors[0][:] = self.bkupColor[:]
        self._visObj.hilight = self.bkupHilight

        if self.IsModal(): self.EndModal(wx.ID_CANCEL)
        else: self.Hide()
        return

    def OnCloseBtn(self, evt):
        """ Closeボタンのイベント.
          evt - wx.CommandEvent.
        """
        if not self._visObj: return
        if self.IsModal(): self.EndModal(wx.ID_OK)
        else: self.Hide()
        return


if __name__ == '__main__':
    class DummyObj:
        def __init__(self):
            self.hilight = 0.5
            self._colors = [ [1.0, 1.0, 1.0, 0.5] ]
        def notice(self):
            pass
        def chkNotice(self):
            pass

    dummy = DummyObj()
    
    app = wx.App()
    dlg = EditPropDlg(None, dummy)
    dlg.Show()
    app.MainLoop()
    
