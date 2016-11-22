#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""

#----------------------------------------------------------------------
"""アライメントタイプ"""
(AL_LEFT, AL_RIGHT, AL_CENTER) = range(3)
"""フォント種別"""
(FONT_LINE, FONT_HELVETICA, FONT_TIMESROMAN) = range(3)

#----------------------------------------------------------------------
import numpy as N
import ctypes as C

import os.path
vfr_impl = N.ctypeslib.load_library('vfr_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))
vfr_impl.gfxLetters_GetTextWidth.restype = C.c_double
vfr_impl.gfxLetters_GetTextWidth.argtypes = [
    C.c_int, C.c_char_p, C.c_double]

vfr_impl.gfxLetters_DrawLetter.restype = C.c_double
vfr_impl.gfxLetters_DrawLetter.argtypes = [
    C.c_int, C.c_char, C.c_double]


#----------------------------------------------------------------------
from gfxNode import *
from utilMath import *

class Letters(GfxNode):
    """
    テキストグリフクラス
    Lettersクラスは，文字(テキストグリフ)を表示するシーングラフノードクラスです．
    テキストグリフはストロークフォントによって表示され，通常のシーングラフノード同様，
    視点からの距離，角度に応じたレンダリングが適用されます．
      font: フォント種別(FONT_LINE, FONT_HELVETICA, FONT_TIMESROMAN)
      textBuf: 表示文字列
      alignType: アライメントタイプ(AL_LEFT, AL_RIGHT, AL_CENTER)
      fontScale: 文字フォントスケール
      spaceRate: 文字間隔比率
    """
    def __init__(self, name =Node._NONAME, suicide =False, font =FONT_LINE):
        GfxNode.__init__(self, name, suicide)
        self.font = font
        self.textBuf = ""
        self.alignType = AL_LEFT
        self.fontScale = 1.0
        self.spaceRate = 0.05

    def setLetters(self, str):
        """
        表示文字列を設定する
        - str: 表示文字列
        """
        self.textBuf = str
        self.generateBbox()
        self.notice()

    def getTextWidth(self):
        """
        表示文字列の幅を返す
        """
        ret = vfr_impl.gfxLetters_GetTextWidth(self.font,
                                               self.textBuf, self.spaceRate)
        return ret
        
    def getTextHeight(self):
        """
        表示文字列の高さを返す
        """
        if self.font == FONT_LINE:
            return 0.9
        elif self.font == FONT_HELVETICA:
            return 1.68
        elif self.font == FONT_TIMESROMAN:
            return 0.727
        return 1.0

    def getNumLines(self):
        """
        表示文字列の行数を返す
        """
        nl = 1
        for i in range(len(self.textBuf)):
            if self.textBuf[i] == '\n':
                nl = nl + 1
        return nl

    def generateBbox(self):
        """
        バウンディングボックス再計算
        """
        tw = self.getTextWidth()
        thx = 1.0
        if self.font == FONT_HELVETICA: thx = 0.5
        self._bbox[0][0] = 0.0
        self._bbox[1][0] = tw * self.fontScale
        if self.alignType == AL_CENTER:
            self._bbox[0][0] = self._bbox[0][0] - 0.5 * tw * self.fontScale
            self._bbox[1][0] = self._bbox[1][0] - 0.5 * tw * self.fontScale
        elif self.alignType == AL_RIGHT:
            self._bbox[0][0] = self._bbox[0][0] - tw * self.fontScale
            self._bbox[1][0] = self._bbox[1][0] - tw * self.fontScale
        self._bbox[0][1] = - self.getTextHeight() * \
                           self.fontScale * (self.getNumLines() - thx)
        self._bbox[1][1] = self.getTextHeight() * self.fontScale * thx
        self._bbox[0][2] = self._bbox[1][2] = 0.0

    def renderSolid(self):
        """
        ソリッドレンダリング
        """
        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # draw
        glDisable(GL_LIGHTING)
        glNormal3f(0.0, 0.0, 1.0)
        glPushMatrix()
        glScalef(self.fontScale, self.fontScale, self.fontScale)

        tw = (self._bbox[1][0] - self._bbox[0][0]) / self.fontScale
        if self.alignType == AL_RIGHT:
            glTranslatef(-tw, 0.0, 0.0)
        elif self.alignType == AL_CENTER:
            glTranslatef(-0.5*tw, 0.0, 0.0)

        transltd = 0.0
        for i in range(len(self.textBuf)):
            if self.textBuf[i] == '\n':
                glTranslatef(-transltd, -self.getTextHeight(), 0.0)
                transltd = 0.0
            else:
                ret = vfr_impl.gfxLetters_DrawLetter(self.font,
                                                     self.textBuf[i],
                                                     self.spaceRate)
                transltd = transltd + ret

        glPopMatrix()
        glEnable(GL_LIGHTING)

        # end display-list definition
        self.endDispList(DLF_SOLID)
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        """
        self.renderSolid()
