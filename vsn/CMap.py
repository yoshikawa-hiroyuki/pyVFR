#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
""" CMap
  CMapダイアログクラス, CMapBarクラス, CMapCanvasクラス,
  CMapConfirmダイアログクラスを提供します.
"""
""" Color map editor dialog / Color map confirm dialog.
"""

import wx
import os
try:
    from wx import glcanvas
    haveGlCanvas = True
except ImportError:
    haveGlCanvas = False
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    haveOpenGl = True
except ImportError:
    haveOpenGl = False


import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr.lut import *
import App


#----------------------------------------------------------------
# class CMapBar
#----------------------------------------------------------------

class CMapBar(wx.Window):
    """ Color map windowクラス
    """
    def __init__(self, parent, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, showLut=True,  showAlpha=False):
        """ 初期設定.
          parent - wx.Window. 親widget.
          pos - Point. position.
          size - Size.
        """
        wx.Window.__init__(self, parent, -1, pos, size,
                           wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.lut = Lut()
        self.colour = [1.0, 1.0, 1.0, 1.0]
        self.hilight = 0.0
        self.showLut = showLut
        self.showAlpha = showAlpha

        # bind to event
        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def setLut(self, lut):
        """ Lutの設定.
          lut - Lut. カラールックアップテーブル.
        """
        self.lut.setTo(lut)
        self.lut.normalize()
        self.Refresh(False)

    def OnPaint(self, event):
        """ 描画処理イベント.
          event - wx.Event.
        """
        if not self.lut: return
        dc = wx.PaintDC(self)
        pen = wx.Pen(wx.Colour())
        pen.SetWidth(1)
        brush = wx.Brush(colour=wx.Colour())
        
        sz = self.GetSize()
        delta = sz.GetWidth() / self.lut.numEntry
        h = sz.GetHeight()

        if self.showLut:
            for i in range(self.lut.numEntry):
                iR = int((self.lut.entry[i, 0]) * 255.0)
                iG = int((self.lut.entry[i, 1]) * 255.0)
                iB = int((self.lut.entry[i, 2]) * 255.0)
                pen.SetColour(wx.Colour(iR, iG, iB))
                dc.SetPen(pen)
                dc.DrawLine(int(i*delta), 0, int(i*delta), h)
                continue # end of for i

            if self.showAlpha:
                ha = int(h / 3)
                for i in range(self.lut.numEntry):
                    idv = int(self.lut.entry[i, 3] * 255.0)
                    pen.SetColour(wx.Colour(idv, idv, idv))
                    dc.SetPen(pen)
                    dc.DrawLine(int(i*delta), 0, int(i*delta), ha)
                    continue # end of for i
        else:
            w3 = int(sz.GetWidth() / 3) + 1
            # base color
            col = wx.Colour(int(self.colour[0]*255),
                            int(self.colour[1]*255), int(self.colour[2]*255))
            pen.SetColour(col)
            dc.SetPen(pen)
            brush.SetColour(col)
            dc.SetBrush(brush)
            dc.DrawRectangle(0, 0, w3, h)
            # base alpha
            col = wx.Colour(int(self.colour[3]*255),
                            int(self.colour[3]*255), int(self.colour[3]*255))
            pen.SetColour(col)
            dc.SetPen(pen)
            brush.SetColour(col)
            dc.SetBrush(brush)
            dc.DrawRectangle(w3 -1, 0, w3, h)
            # hilight
            col = wx.Colour(int(self.hilight*255),
                            int(self.hilight*255), int(self.hilight*255))
            pen.SetColour(col)
            dc.SetPen(pen)
            brush.SetColour(col)
            dc.SetBrush(brush)
            dc.DrawRectangle(w3 * 2 -2, 0, w3, h)

        return


#----------------------------------------------------------------
# class CMapCanvas
#----------------------------------------------------------------
(cnlRED, cnlGREEN, cnlBLUE, cnlALPHA) = range(4)

class CMapCanvas(glcanvas.GLCanvas):
    """ Color map GLcanvasクラス
    """
    def __init__(self, parent, cmDlg, ID=-1,
                 pos=wx.DefaultPosition, size=wx.DefaultSize):
        """ 初期設定.
          parent - wx.Window. 親widget
          pos - Point. position.
          size - Size
        """
        attrLst = (wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER,
                   wx.glcanvas.WX_GL_DEPTH_SIZE, 1)
        glcanvas.GLCanvas.__init__(self, parent=parent, id=ID,
                                   pos=pos, size=size, attribList=attrLst)
        self.ctx = glcanvas.GLContext(self)
        self.parent = parent
        self.refDlg = cmDlg
        self.rgbaCnl = cnlRED
        self.lastX = -1
        self.lut = Lut()
        
        # bind to event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)


    def setLut(self, lut):
        """ Lutの設定.
          lut - Lut. カラールックアップテーブル.
        """
        self.lut.setTo(lut)
        self.Refresh(False)
        return

    def setRGBAChannel(self, cnl):
        if self.rgbaCnl == cnl: return
        self.rgbaCnl = cnl
        self.Refresh(False)
        return

    def OnPaint(self, event):
        """ 描画処理イベント.
          event - wx.Event.
        """
        dc = wx.PaintDC(self)

        #if not self.GetContext(): return
        self.SetCurrent(self.ctx)

        # draw
        glClearColor(0.858, 0.858, 0.439, 0.0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        if self.lut.numEntry < 1: return
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        cOff = self.rgbaCnl
        yed = 0.15
        y = dx = 2.0 / self.lut.numEntry

        glBegin(GL_QUADS)
        for i in range(self.lut.numEntry):
            if self.rgbaCnl == cnlALPHA:
                dv = self.lut.entry[i, cOff]
                dv = 2.0*dv - dv*dv
                colorv = [dv, dv, dv]
            else:
                colorv = [0.0, 0.0, 0.0]
                colorv[cOff] = self.lut.entry[i, cOff]
            glColor3f(colorv[0], colorv[1], colorv[2])

            y = (2.0 - yed*2.0) * self.lut.entry[i, cOff] - (1.0 - yed)
            glVertex3f(-1.0 + i*dx,     -1.0+yed, 0.0)
            glVertex3f(-1.0 + (i+1)*dx, -1.0+yed, 0.0)
            glVertex3f(-1.0 + (i+1)*dx,  y,       0.0)
            glVertex3f(-1.0 + i*dx,      y,       0.0)

        # paint band
        glColor3f(0.3, 0.3, 0.2)
        glVertex3f(-1.0, -1.0,     0.0)
        glVertex3f( 1.0, -1.0,     0.0)
        glVertex3f( 1.0, -1.0+yed, 0.0)
        glVertex3f(-1.0, -1.0+yed, 0.0)
        glVertex3f(-1.0, 1.0-yed, 0.0)
        glVertex3f( 1.0, 1.0-yed, 0.0)
        glVertex3f( 1.0, 1.0,     0.0)
        glVertex3f(-1.0, 1.0,     0.0)

        glEnd()

        # flush
        glFlush()
        # swap
        self.SwapBuffers()

    def OnSize(self, event):
        """ サイズ変更のイベント.
          event - wx.Event.
        """
        #glcanvas.GLCanvas.OnSize(event)
        sz = self.GetClientSize()
        #if not self.GetContext(): return
        #self.SetCurrent(self.ctx)
        glViewport(0, 0, sz.x, sz.y)
        
    def OnEraseBackground(self, event):
        """ Erase backgroundイベント.
          event - wx.Event.
        """
        return

    def OnMouse(self, event):
        """ マウスボタンイベント.
          event - wx.MouseEvent.
        """
        sz = self.GetClientSize()

        if event.Dragging() or event.ButtonUp() or event.ButtonDown() or \
           (event.Leaving() and (event.LeftIsDown() or event.RightIsDown())):
            wsz = sz.GetWidth()
            hsz = sz.GetHeight()
            evposx = CLAMP(0, wsz, event.GetX())
            evposy = CLAMP(0, hsz, event.GetY())
            cOff = self.rgbaCnl
            yed = 0.15
            yedpx = float(hsz) * yed / (2.0 + yed *2.0)
            x = long(evposx * (self.lut.numEntry - 1.0) / wsz)
            y = (float(hsz) - evposy - yedpx) / (hsz - yedpx * 2.0)
            if x < 0: x = 0
            elif x > 255: x = 255
            if y < 0.0: y = 0.0
            elif y > 1.0: y = 1.0

            self.lut.entry[x, cOff] = y
            self.lut.isStdLut = False

            if event.Dragging() and self.lastX >= 0:
                if self.lastX < x:
                    a = (y - self.lut.entry[self.lastX, cOff]) \
                        / (x - self.lastX)
                    b = self.lut.entry[self.lastX, cOff] - a * self.lastX
                    for i in range(self.lastX+1, x):
                        self.lut.entry[i, cOff] = a * i + b
                elif self.lastX > x:
                    a = (self.lut.entry[self.lastX, cOff] - y) \
                        / (self.lastX - x)
                    b = y - a * x
                    for i in range(x+1, self.lastX):
                        self.lut.entry[i, cOff] = a * i + b
            self.lastX = x
            self.Refresh(False)

        if event.ButtonUp() or \
           (event.Leaving() and (event.LeftIsDown() or event.RightIsDown())):
            if self.refDlg: self.refDlg.setLut(self.lut, True)
            self.lastX = -1
            
        return


#----------------------------------------------------------------
# class CMapDlg
#----------------------------------------------------------------

class CMapDlg(wx.Dialog):
    """ Color mapダイアログクラス
     CMapCanvas, CMapBarを用いたcolor mapのUIを提供します.
    """
    def __init__(self, parent, app, ID=-1, title="CMapDlg"):
        """ 初期設定.
          parent - wx.Window. 親widget.
          app - App.
          ID - int. ID.
          title - String. ダイアログの表題.
        """
        wx.Dialog.__init__(self, parent, ID, title)
        self.parent = parent
        self.app = app
        self.lut = Lut()
        self.lut_back = Lut()
        self.lutImpDir = ""

        # prepare objects
        self.glCanvas = CMapCanvas(self, self)
        self.cMapBar = CMapBar(self, size=(256,25))

        ritems = ('red', 'green', 'blue', 'alpha')
        channelRadio = wx.RadioBox(self, -1, 'Color channel',
                                   choices=ritems, style=wx.RA_VERTICAL)

        importBtn = wx.Button(self, -1, 'Import')
        exportBtn = wx.Button(self, -1, 'Export')
        rampBtn = wx.Button(self, -1, 'Ramp')
        invertBtn = wx.Button(self, -1, 'Invert')
        copyBtn = wx.Button(self, -1, 'Copy')
        resetBtn = wx.Button(self, -1, 'Reset')
        cancelBtn = wx.Button(self, -1, 'Cancel')
        closeBtn = wx.Button(self, -1, 'Close')

        # bind to event
        channelRadio.Bind(wx.EVT_RADIOBOX, self.OnChannelRadio)
        importBtn.Bind(wx.EVT_BUTTON, self.OnImportBtn)
        exportBtn.Bind(wx.EVT_BUTTON, self.OnExportBtn)
        rampBtn.Bind(wx.EVT_BUTTON, self.OnRampBtn)
        invertBtn.Bind(wx.EVT_BUTTON, self.OnInvertBtn)
        copyBtn.Bind(wx.EVT_BUTTON, self.OnCopyBtn)
        resetBtn.Bind(wx.EVT_BUTTON, self.OnResetBtn)
        cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelBtn)
        closeBtn.Bind(wx.EVT_BUTTON, self.OnCloseBtn)

        # sizer layout
        topsizer = wx.BoxSizer(wx.HORIZONTAL)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.glCanvas, 1, wx.EXPAND|wx.ALL, 5)
        vsizer.Add(self.cMapBar, 0, wx.EXPAND|wx.ALL, 5)
        topsizer.Add(vsizer, 0, wx.EXPAND|wx.ALL)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(channelRadio, 1, wx.EXPAND|wx.ALL, 3)
        vsizer2 = wx.BoxSizer(wx.VERTICAL)
        hsizer.Add(vsizer2, 0, wx.ALL, 0)
        vsizer2.Add(importBtn, 0, wx.EXPAND|wx.ALL, 3)
        vsizer2.Add(exportBtn, 0, wx.EXPAND|wx.ALL, 3)
        vsizer.Add(hsizer, 0, wx.EXPAND|wx.ALL, 0)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(rampBtn, 1, wx.EXPAND|wx.ALL, 3)
        hsizer.Add(invertBtn, 1, wx.EXPAND|wx.ALL, 3)
        vsizer.Add(hsizer, 0, wx.EXPAND|wx.ALL, 0)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(copyBtn, 1, wx.EXPAND|wx.ALL, 3)
        hsizer.Add(resetBtn, 1, wx.EXPAND|wx.ALL, 3)
        vsizer.Add(hsizer, 0, wx.EXPAND|wx.ALL, 0)
        
        staticln = wx.StaticLine(self, -1, size=(5, 5))
        vsizer.Add(staticln, 0, wx.EXPAND|wx.ALL)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(cancelBtn, 1, wx.EXPAND|wx.ALL, 3)
        hsizer.Add(closeBtn, 1, wx.EXPAND|wx.ALL, 3)
        vsizer.Add(hsizer, 0, wx.EXPAND|wx.ALL, 0)
        
        topsizer.Add(vsizer, 0, wx.EXPAND|wx.ALL)

        # post process
        self.SetAutoLayout(True)
        self.SetSizer(topsizer)
        topsizer.SetSizeHints(self)
        topsizer.Fit(self)

        return


    def initLut(self, lut):
        """ Lutのバックアップと設定.
          lut - Lut. 新しいカラールックアップテーブル.
        """
        self.lut_back.setTo(lut)
        self.setLut(lut)


    def setLut(self, lut, updRef=False):
        """ Lutの設定.
          lut - Lut. カラールックアップテーブル.
          updRef - bool. True:参照Lutを更新する, False:しない.
        """
        self.lut.setTo(lut)

        if self.glCanvas:
            self.glCanvas.setLut(self.lut)
        if self.cMapBar:
            self.cMapBar.setLut(self.lut)
            
        if updRef:
            self.updateRef()
        return


    def updateRef(self):
        """ 参照Lutの更新.
          戻り値 -> bool. 失敗ならFalseを返す.
        """
        if self.app:
            self.app.Refresh()
        return


    def OnChannelRadio(self, event):
        obj = event.GetEventObject()
        sel = obj.GetSelection()
        self.glCanvas.setRGBAChannel(sel)
        return
        
    def OnImportBtn(self, event):
        """ Importボタンのイベント.
         event - wx.CommandEvent.
        """
        fileDlg = wx.FileDialog(self, 'select lut file to import',
                                "", "", 'lut file (*.lut)|*.lut|(*)|*',
                                wx.OPEN)
        if self.lutImpDir != "":
            fileDlg.SetDirectory(App.ConvSysToWx(self.lutImpDir))

        if fileDlg.ShowModal() != wx.ID_OK: return
        inPath = fileDlg.GetPath()
        if inPath == "": return

        # load lut
        try:
            xlut = lut.Lut()
            with open(inPath, 'r') as ifd:
                if not xlut.importStream(ifd):
                    msg = 'Import colormap: can\'t load lut file: ' + inPath
                    wx.MessageBox(msg)
                    return
            self.setLut(xlut, True)
            self.lutImpDir = os.path.dirname(inPath)
        except:
            msg = 'Import colormap: can\'t open lut file: ' + inPath
            wx.MessageBox(msg)

        return

    def OnExportBtn(self, event):
        """ Exportボタンのイベント.
         event - wx.CommandEvent.
        """
        fileDlg = wx.FileDialog(self, 'select lut file to export',
                                "", "", 'lut file (*.lut)|*.lut|(*)|*',
                                wx.SAVE)
        if self.lutImpDir != "":
            fileDlg.SetDirectory(App.ConvSysToWx(self.lutImpDir))

        if fileDlg.ShowModal() != wx.ID_OK: return
        outPath = fileDlg.GetPath()
        if outPath == "": return

        if os.path.isfile(outPath):
            msg = 'The specified file has already existed\n  ' \
                  + outPath + '\n\nAre you sure to override ?\n'
            msgDlg = wx.MessageDialog(None, App.ConvSysToWx(msg),
                                      'Export colormap',
                                      wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            if msgDlg.ShowModal() != wx.ID_OK: return
        try:
            with open(outPath, 'w') as ofd:
                if not self.lut.exportStream(ofd):
                    msg = 'Export colormap: can\'t export lut file: ' + outPath
                    wx.MessageBox(msg)
                    return
        except:
            msg = 'Export colormap: can\'t open lut file: ' + outPath
            wx.MessageBox(msg)

        return

    def OnRampBtn(self, event):
        """ Rampボタンのイベント.
         event - wx.CommandEvent.
        """
        if not self.glCanvas: return
        
        rlut = Lut(); rlut.setTo(self.lut)
        cOff = self.glCanvas.rgbaCnl
        for i in range(rlut.numEntry):
            rlut.entry[i, cOff] = float(i) / (rlut.numEntry - 1)
        rlut.isStdLut = False

        self.setLut(rlut, True)


    def OnInvertBtn(self, event):
        """ Invertボタンのイベント.
         event - wx.CommandEvent.
        """
        if not self.glCanvas: return
        
        rlut = Lut(); rlut.setTo(self.lut)
        cOff = self.glCanvas.rgbaCnl
        for i in range(int(rlut.numEntry/2)):
            x = rlut.entry[i, cOff]
            rlut.entry[i, cOff] = rlut.entry[(rlut.numEntry-1-i), cOff]
            rlut.entry[(rlut.numEntry-1-i), cOff] = x
        rlut.isStdLut = False

        self.setLut(rlut, True)


    def OnCopyBtn(self, event):
        pass
        
    def OnResetBtn(self, event):
        """ Resetボタンのイベント.
         event - wx.CommandEvent.
        """
        if not self.glCanvas: return
        lut0 = Lut()
        self.setLut(lut0, True)


    def OnCancelBtn(self, event):
        """ Cancelボタンのイベント.
         event - wx.CommandEvent.
        """
        self.setLut(self.lut_back, True)
        self.Hide()

    def OnCloseBtn(self, event):
        """ Closeボタンのイベント.
         event - wx.CommandEvent.
        """
        self.Hide()


class MyApp(wx.App):
    def OnInit(self):
        dlg = CMapDlg(None, None)
        dlg.ShowModal()
        dlg.Destroy()
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
