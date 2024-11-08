#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""


#----------------------------------------------------------------------
def hsv2rgb(hsv):
    """
    HSV/RGB変換
    HSV表現の色データをRGB表現に変換し，返すユーティリティ関数です．
    - hsv: HSVカラー(0〜1)
    """
    if len(hsv) < 3 : return [0.0, 0.0, 0.0]
    h = hsv[0]
    if hsv[2] == 0.0 :
        return [0.0, 0.0, 0.0]
    elif hsv[1] == 0.0 :
        return [hsv[2], hsv[2], hsv[2]]
    h = h* 6.0
    if h >= 6.0 : h = 0.0
    i = int(h)
    f = h - i
    p = hsv[2]*(1.0 - hsv[1])
    q = hsv[2]*(1.0 - hsv[1]*f)
    t = hsv[2]*(1.0 - hsv[1]*(1.0 - f))
    if i == 0:
        rgb = [hsv[2], t, p]
    elif i == 1:
        rgb = [q, hsv[2], p]
    elif i == 2:
        rgb = [p, hsv[2], t]
    elif i == 3:
        rgb = [p, q, hsv[2]]
    elif i == 4:
        rgb = [t, p, hsv[2]]
    elif i == 5:
        rgb = [hsv[2], p, q]
    return rgb

def CLAMP(x, y, z):
    """ (x > z) ? x : ((y < z) ? y : z) と同様.
    """
    v = z
    if x > z: v = x
    elif y < z: v = y
    return v

        
#----------------------------------------------------------------------
import copy
import numpy as N

"""カラーエントリー最大値"""
LUT_MAX_ENTRY = 256

class Lut(object):
    """
    Lutは，カラールックアップテーブルを表現するクラスの実装です．
    カラーエントリーテーブルと，データのレンジで構成されます．
      numEntry: カラーエントリー数
      minVal: データの最小値
      maxVal: データの最大値
      entry: カラーエントリーテーブル(ctypes.c_float * 4 * numEntry)
      isStdLut: デフォルトカラーマップかどうか
    """
    def __init__(self):
        global LUT_MAX_ENTRY
        self.numEntry = LUT_MAX_ENTRY
        self.minVal = 0.0
        self.maxVal = 1.0
        self.entry = N.zeros((LUT_MAX_ENTRY, 4), dtype=float)
        self.isStdLut = False
        self.setDefault()

    def alcEntry(self, numEntry):
        """
        カラーエントリーテーブル領域を確保する．
        - numEntry: 確保するカラーエントリーテーブルのサイズ
        """
        if numEntry < 0: return False
        self.numEntry = numEntry
        self.entry = N.zeros((numEntry, 4), dtype=float)
        self.isStdLut = False
        return True

    def setTo(self, lut):
        """
        代入
        """
        if not self.alcEntry(lut.numEntry):
            raise AttributeError('alloc failed.')
        self.minVal = lut.minVal
        self.maxVal = lut.maxVal
        self.entry = lut.entry.copy()
        self.isStdLut = lut.isStdLut
        
    def setDefault(self):
        """
        デフォルトカラーテーブルに設定する
        """
        x = 0.666667 / (self.numEntry-1)
        y = 1.0 / (self.numEntry-1)
        for i in range(self.numEntry):
            rgb = hsv2rgb([0.666667 - i*x, 1.0, 1.0])
            self.entry[i, 0] = rgb[0]
            self.entry[i, 1] = rgb[1]
            self.entry[i, 2] = rgb[2]
            self.entry[i, 3] = i*y
        self.isStdLut = True
        return

    def normalize(self):
        """ 正規化.
          色成分の格納数を256個に正規化します.
          戻り値 -> boolean.
        """
        if self.numEntry < 1: return False
        if self.numEntry == LUT_MAX_ENTRY: return True
        org = copy.deepcopy(self)
        self.numEntry = LUT_MAX_ENTRY

        for i in range(LUT_MAX_ENTRY):
            oi = self.numEntry * i / LUT_MAX_ENTRY
            self.entry[i, 0] = org.entry[oi, 0]
            self.entry[i, 1] = org.entry[oi, 1]
            self.entry[i, 2] = org.entry[oi, 2]
            self.entry[i, 3] = org.entry[oi, 3]
        return True

    def getValIdx(self, val):
        """
        データ値に対応するカラーエントリーテーブルのインデックスを返す．
        entry[インデックス*4]〜entry[インデックス*4 +3]が対応する色である．
        - val: データ値
        """
        if val >= self.maxVal: return (self.numEntry-1)
        if val <= self.minVal: return 0
        if self.maxVal <= self.minVal: return 0
        if not (val >= self.minVal and val <= self.maxVal): return 0
        return int((self.numEntry-1)*(val-self.minVal)
                   / (self.maxVal-self.minVal))

    def getList(self):
        return self.entry.reshape((self.numEntry*4)).tolist()

    def exportStream(self, ofd, ts=0):
        """ 文字列ストリームへの出力.
          戻り値 -> boolean.
          ofd - stream
          ts - 字下げ数
        """
        if not ofd: return False
        if self.numEntry < 1: return False
        tsStr = ' ' * ts
        fstr = tsStr + str(self.minVal) + ' ' + str(self.maxVal) + '\n'
        ofd.write(fstr)
        for i in range(self.numEntry):
            fstr = tsStr \
                   + str(CLAMP(0.0, 1.0, self.entry[i, 0])) + ' ' \
                   + str(CLAMP(0.0, 1.0, self.entry[i, 1])) + ' ' \
                   + str(CLAMP(0.0, 1.0, self.entry[i, 2])) + ' ' \
                   + str(CLAMP(0.0, 1.0, self.entry[i, 3])) + '\n'
            ofd.write(fstr)
        return True

    def importStream(self, ifd):
        """ 文字列ストリームからの入力.
          戻り値 -> boolean.
          ifd - stream
        """
        if not ifd: return False

        line = ifd.readline()
        data = line.strip().split()
        if len(data) < 2: return False
        self.minVal = float(data[0])
        self.maxVal = float(data[1])

        if not self.alcEntry(LUT_MAX_ENTRY):
            return False

        numLines = 0
        lines = ifd.readlines()
        for line in lines:
            data = line.strip().split()
            if len(data) < 3: return False
            r = float(data[0])
            g = float(data[1])
            b = float(data[2])
            a = 1.0
            if (len(data) > 3): a = float(data[3])
            self.entry[numLines, 0] = CLAMP(0.0, 1.0, r)
            self.entry[numLines, 1] = CLAMP(0.0, 1.0, g)
            self.entry[numLines, 2] = CLAMP(0.0, 1.0, b)
            self.entry[numLines, 3] = CLAMP(0.0, 1.0, a)
            numLines += 1
            if numLines == LUT_MAX_ENTRY:
                break

        self.isStdLut = False
        self.numEntry = numLines
        if self.numEntry < 1: return False
        return True
