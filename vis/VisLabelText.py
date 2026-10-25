#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegBounds
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *
import App

#----------------------------------------------------------------------
class VisLabelText(VisObj):
    """ VisLabelTextクラス
        show text label base class
    """
    def __init__(self, **args):
        """
        args: font =FONT_LINE, textBuf ="", alignType =AL_LEFT,
              fontScale =1.0, spaceRate =0.05
        """
        VisObj.__init__(self, **args)

        self.showType = gfxNode.RT_WIRE
        if 'font' in args and args['font'] != letters.FONT_LINE:
            self.showType = gfxNode.RT_SHADING
        
        self._letters = letters.Letters(args)

        if self.update(**args):
            self.show = True
        return

    def __del__(self):
        VisObj.__del__(self)
        if not self._letters is None:
            del self._letters
            self._letters = None
        return

    def update(self, **args):
        self.show = False
        if self._letters is None:
            return False

        # pickup args
        font = None if not 'font' in args else args['font']
        textBuf = None if not 'textBuf' in args else args['textBuf']
        alignType = None if not 'alignType' in args else args['alignType']
        fontScale = None if not 'fontScale' in args else args['fontScale']
        spaceRate = None if not 'spaceRate' in args else args['spaceRate']

        # set parameters to _letters
        if not font is None:
            self._letters.font = font
            if font == letters.FONT_LINE:
                self.showType = gfxNode.RT_WIRE
            else:
                self.showType = gfxNode.RT_SHADING
            self._letters.notice()
        if not textBuf is None:
            self._letters.setLetters(textBuf)
        if not alignType is None:
            self._letters.alignType = alignType
            self._letters.notice()            
        if not fontScale is None:
            self._letters.fontScale = fontScale
            self._letters.notice()            
        if not spaceRate is None:
            self._letters.spaceRate = spaceRate
            self._letters.notice()

        self.generateBbox()
        self.show = True
        return True
        
    
    def initPP(self):
        if not self.paramsPnl:
            return False

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # font
        self._fontButtons = []
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='font'))
        fontChoices = ["LINE", "HELVETICA", "TIMESROMAN"]
        for i, choice in enumerate(fontChoices):
            style = wx.RB_GROUP if i == 0 else 0
            rb = wx.RadioButton(self.paramsPnl, label=choice, style=style)
            rb.Bind(wx.EVT_RADIOBUTTON, self.OnFontRadio)
            sizerH.Add(rb, flag=wx.ALL, border=3)
            self._fontButtons.append(rb)
            continue # for i,choice

        # textBuff
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='label text'))
        self._textBuffTxt = wx.TextCtrl(self.paramsPnl, value='', \
                                        size=wx.Size(-1, 30), \
                                        style=wx.TE_PROCESS_ENTER | \
                                        wx.TE_MULTILINE)
        sizerH.Add(self._textBuffTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._textBuffTxt.Bind(wx.EVT_TEXT_ENTER, self.OnTextBuffTxt)

        # alignType
        self._alignButtons = []
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='align'))
        alignChoices = ["LEFT", "RIGHT", "CENTER"]
        for i, choice in enumerate(alignChoices):
            style = wx.RB_GROUP if i == 0 else 0
            rb = wx.RadioButton(self.paramsPnl, label=choice, style=style)
            rb.Bind(wx.EVT_RADIOBUTTON, self.OnAlignRadio)
            sizerH.Add(rb, flag=wx.ALL, border=3)
            self._alignButtons.append(rb)
            continue # for i,choice

        # fontScale
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='font scale'))
        self._fontScaleTxt = wx.TextCtrl(self.paramsPnl, value='1.0', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._fontScaleTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._fontScaleTxt.Bind(wx.EVT_TEXT_ENTER, self.OnFontScaleTxt)

        # spaceRate
        sizerH = wx.BoxSizer()
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)
        sizerH.Add(wx.StaticText(self.paramsPnl, label='space rate'))
        self._spaceRateTxt = wx.TextCtrl(self.paramsPnl, value='0.05', \
                                         style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self._spaceRateTxt, flag=wx.EXPAND|wx.ALL, proportion=1, \
                   border=3)
        self._spaceRateTxt.Bind(wx.EVT_TEXT_ENTER, self.OnSpaceRateTxt)

        # sizing
        self.paramsPnl.SetSizer(sizerTop)
        sizerTop.Fit(self.paramsPnl)
        self.paramsPnl.Fit()

        return True

    def updatePP(self):
        if self.paramsPnl is None or self._letters is None:
            return False

        # font
        if self._letters.font == letters.FONT_LINE:
            self._fontButtons[0].SetValue(True)
        elif self._letters.font == letters.FONT_HELVETICA:
            self._fontButtons[1].SetValue(True)
        elif self._letters.font == letters.FONT_TIMESROMAN:
            self._fontButtons[2].SetValue(True)

        # textBuff
        self._textBuffTxt.SetValue(self._letters.textBuf)

        # alignType
        if self._letters.font.alignType == gfxNode.AL_LEFT:
            self._alignButtons[0].SetValue(True)
        elif self._letters.font.alignType == gfxNode.AL_RIGHT:
            self._alignButtons[1].SetValue(True)
        elif self._letters.font.alignType == gfxNode.AL_CENTER:
            self._alignButtons[2].SetValue(True)

        # fontScale
        self._fontScaleTxt.SetValue(str(self._letters.fontScale))

        # spaceRate
        self._spaceRateTxt.SetValue(str(self._letters.spaceRate))

        return True

    # Event Handlers

    def OnFontRadio(self, event):
        new_fontType = None
        if self._fontButtons[0].GetValue() == True:
            new_fontType = letters.FONT_LINE
        elif self._fontButtons[1].GetValue() == True:
            new_fontType = letters.FONT_HELVETICA
        elif self._fontButtons[2].GetValue() == True:
            new_fontType = letters.FONT_TIMESROMAN

        if new_fontType is None:
            new_fontType = letters.FONT_LINE
            self._fontButtons[0].SetValue(True)

        if self.update(font=new_fontType):
            self.chkNotice()
        return

    def OnTextBuffTxt(self, event):
        val = self._textBuffTxt.GetValue()
        if self.update(textBuf=val):
            self.chkNotice()
        return

    def OnAlignRadio(self, event):
        new_alignType = None
        if self._alignButtons[0].GetValue() == True:
            new_alignType = gfxNode.AL_LEFT
        elif self._alignButtons[1].GetValue() == True:
            new_alignType = gfxNode.AL_RIGHT
        elif self._alignButtons[2].GetValue() == True:
            new_alignType = gfxNode.AL_CENTER

        if new_alignType is None:
            new_fontType = gfxNode.AL_LEFT
            self._alignButtons[0].SetValue(True)

        if self.update(alignType=new_alignType):
            self.chkNotice()
        return

    def OnFontScaleTxt(self, event):
        try:
            val = float(self._fontScaleTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val <= 0.0:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if self.update(fontScale=val):
            self.chkNotice()
        return

    def OnSpaceRateTxt(self, event):
        try:
            val = float(self._spaceRateTxt.GetValue())
        except:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if val <= 0.0:
            wx.MessageBox('Invalid value specified.', 'Error', style=wx.OK)
            self.updatePP()
            return
        if self.update(spaceRate=val):
            self.chkNotice()
        return

#----------------------------------------------------------------------
class VisLabel2D(VisLabelText):
    """ VisLabel2Dクラス
        show text label in 2D View
    """
    def __init__(self, **args):
        VisLabelText.__init__(self)
        if not self._letters is None:
            app = App.GetVsnApp()
            camera = app.getCamera()
            camera.addToFront(self._letters)
        return
    
    def getVisObjType(self):
        return "Label2D"


#----------------------------------------------------------------------
class VisLabel3D(VisLabelText):
    """ VisLabel3Dクラス
        show text label in 2D View
    """
    def __init__(self, **args):
        VisLabelText.__init__(self)
        if not self._letters is None:
            self.addChild(self._letters)
        return

    def getVisObjType(self):
        return "Label3D"

    
