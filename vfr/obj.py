#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""

#----------------------------------------------------------------------
import ctypes as C
import numpy as N

import os.path
vfr_impl = N.ctypeslib.load_library('vfr_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))
vfr_impl.ObjData_Create.restype = C.c_void_p
vfr_impl.ObjData_Delete.argtypes = [C.c_void_p]

vfr_impl.ObjData_AlcVerts.argtypes = [C.c_void_p, C.c_int]
vfr_impl.ObjData_AlcVerts.restype = C.c_int
vfr_impl.ObjData_AlcNormals.argtypes = [C.c_void_p, C.c_int]
vfr_impl.ObjData_AlcNormals.restype = C.c_int
vfr_impl.ObjData_AlcIndices.argtypes = [C.c_void_p, C.c_int]
vfr_impl.ObjData_AlcIndices.restype = C.c_int
vfr_impl.ObjData_AlcColors.argtypes = [C.c_void_p, C.c_int]
vfr_impl.ObjData_AlcColors.restype = C.c_int

vfr_impl.ObjData_GetNumVerts.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetNumVerts.restype = C.c_int
vfr_impl.ObjData_GetNumNormals.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetNumNormals.restype = C.c_int
vfr_impl.ObjData_GetNumIndices.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetNumIndices.restype = C.c_int
vfr_impl.ObjData_GetNumColors.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetNumColors.restype = C.c_int

vfr_impl.ObjData_GetVerts.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetVerts.restype = C.POINTER(C.c_float*3)
vfr_impl.ObjData_GetNormals.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetNormals.restype = C.POINTER(C.c_float*3)
vfr_impl.ObjData_GetIndices.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetIndices.restype = C.POINTER(C.c_int)
vfr_impl.ObjData_GetColors.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetColors.restype = C.POINTER(C.c_float*4)

vfr_impl.ObjData_GenerateBbox.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetBbox.argtypes = [C.c_void_p]
vfr_impl.ObjData_GetBbox.restype = C.POINTER(C.c_float*3)

vfr_impl.ObjData_LoadOBJ.argtypes = [C.c_void_p, C.c_char_p]
vfr_impl.ObjData_LoadOBJ.restype = C.c_int
vfr_impl.ObjData_LoadSLA.argtypes = [C.c_void_p, C.c_char_p]
vfr_impl.ObjData_LoadSLA.restype = C.c_int
vfr_impl.ObjData_LoadSLB.argtypes = [C.c_void_p, C.c_char_p]
vfr_impl.ObjData_LoadSLB.restype = C.c_int


#----------------------------------------------------------------------
from .utilMath import *

class Obj(object):
    """
    オブジェクトデータクラス
    Objクラスは，頂点座標，法線ベクトル，頂点インデックス，色の各データの
    メモリ管理機能を実装したクラスです．
    各データのメモリ管理機能はC++のクラスであるObjDataで実装され，
    ctypesモジュールのAPIインターフェースを介してObjクラスよりコールされます．
      p_impl: 対応するObjDataクラスインスタンスへの参照
          Objクラスの生成時(__init__)にnewされ，Objクラスの破壊時(__del__)に
          deleteされます．
      _verts: 頂点座標配列．ctypes.POINTER(ctypes.c_float*3)です．
      _normals: 法線ベクトル配列．ctypes.POINTER(ctypes.c_float*3)です．
      _colors: 色(RGBA)配列．ctypes.POINTER(ctypes.c_float*4)です．
      _indices: インデックス配列．ctypes.POINTER(ctypes.c_int)です．
      _bbox: バウンディングボックス(頂点座標の存在範囲).
          (utilMath.Vec3, utilMath.Vec3)です.
      nVerts: 頂点データ数
      nNormals: 法線ベクトルデータ数
      nIndices: インデックスデータ数
      nColors: 色データ数
    """
    def __init__(self):
        self.p_impl = vfr_impl.ObjData_Create()
        bb = vfr_impl.ObjData_GetBbox(self.p_impl)
        self._bbox = [Vec3(bb[0]), Vec3(bb[1])]
        self.updateObjImpl()

    def __del__(self):
        vfr_impl.ObjData_Delete(self.p_impl)
        self.p_impl = None

    def alcData(self, nV=-1, nN=-1, nI=-1, nC=-1):
        """
        頂点座標，法線ベクトル，頂点インデックス，色の各データの領域サイズを
        変更します．
        - nV: 確保する頂点座標データ数．-1の場合は変更しません．
        - nN: 確保する法線ベクトルデータ数．-1の場合は変更しません．
        - nI: 確保する頂点インデックスデータ数．-1の場合は変更しません．
        - nC: 確保する色データ数．-1の場合は変更しません．
        """
        ret = vfr_impl.ObjData_AlcVerts(self.p_impl, nV)
        if not ret: return False;
        ret = vfr_impl.ObjData_AlcNormals(self.p_impl, nN)
        if not ret: return False;
        ret = vfr_impl.ObjData_AlcIndices(self.p_impl, nI)
        if not ret: return False;
        ret = vfr_impl.ObjData_AlcColors(self.p_impl, nC)
        if not ret: return False;
        self.updateObjImpl()
        return True

    def updateObjImpl(self):
        """
        ObjDataクラスインスタンスの状態の反映
        対応するObjDataクラスのインスタンスから，頂点座標，法線ベクトル，
        頂点インデックス，色の各データの領域への参照とデータ数を取得し，
        メンバー変数に設定します．
        """
        if not self.p_impl: return
        self._verts = vfr_impl.ObjData_GetVerts(self.p_impl)
        self._normals = vfr_impl.ObjData_GetNormals(self.p_impl)
        self._indices = vfr_impl.ObjData_GetIndices(self.p_impl)
        self._colors = vfr_impl.ObjData_GetColors(self.p_impl)
        self.nVerts = vfr_impl.ObjData_GetNumVerts(self.p_impl)
        if self.nVerts < 0: self.nVerts = 0
        self.nNormals = vfr_impl.ObjData_GetNumNormals(self.p_impl)
        if self.nNormals < 0: self.nNormals = 0
        self.nIndices = vfr_impl.ObjData_GetNumIndices(self.p_impl)
        if self.nIndices < 0: self.nIndices = 0
        self.nColors = vfr_impl.ObjData_GetNumColors(self.p_impl)
        if self.nColors < 0: self.nColors = 0
        return

    def generateBbox(self):
        """
        バウンディングボックス再計算
        頂点座標の存在範囲を求め，_bboxに設定します．
        """
        if not self.p_impl: return False;
        vfr_impl.ObjData_GenerateBbox(self.p_impl)
        bb = vfr_impl.ObjData_GetBbox(self.p_impl)        
        self._bbox[0][:] = bb[0][:]
        self._bbox[1][:] = bb[1][:]
        self.checkBbox()

    def checkBbox(self):
        """
        バウンディングボックスチェック
        _bboxの値について，反転および縮退をチェックします．
        """
        if self._bbox[1][0] < self._bbox[0][0]:
            s = self._bbox[1][0]
            self._bbox[1][0] = self._bbox[0][0]
            self._bbox[0][0] = s
        if self._bbox[1][1] < self._bbox[0][1]:
            s = self._bbox[1][1]
            self._bbox[1][1] = self._bbox[0][1]
            self._bbox[0][1] = s
        if self._bbox[1][2] < self._bbox[0][2]:
            s = self._bbox[1][2]
            self._bbox[1][2] = self._bbox[0][2]
            self._bbox[0][2] = s
        eps = 0.0001
        if self._bbox[1][0] - self._bbox[0][0] < eps:
            self._bbox[0][0] = self._bbox[0][0] - eps
            self._bbox[1][0] = self._bbox[1][0] + eps
        if self._bbox[1][1] - self._bbox[0][1] < eps:
            self._bbox[0][1] = self._bbox[0][1] - eps
            self._bbox[1][1] = self._bbox[1][1] + eps
        if self._bbox[1][2] - self._bbox[0][2] < eps:
            self._bbox[0][2] = self._bbox[0][2] - eps
            self._bbox[1][2] = self._bbox[1][2] + eps
        return


    def loadFile(self, path, fmt):
        """
        形状データファイル入力
        Wavefront OBJ, STL(AsciiおよびBinary)のファイルを読み込みます．
        ファイルの形状データに応じ，各データのアロケーションを行い，
        値を設定します．
        - path: 形状データファイルのパス
        - fmt: 形状データのフォーマット
               'obj': Wavefront OBJ, 'sla': STL/Ascii, 'slb': STL/Binary
        """
        if not self.p_impl: return False;
        if fmt == 'obj':
            ret = vfr_impl.ObjData_LoadOBJ(self.p_impl, path.encode('utf-8'))
        elif fmt == 'sla':
            ret = vfr_impl.ObjData_LoadSLA(self.p_impl, path.encode('utf-8'))
        elif fmt == 'slb':
            ret = vfr_impl.ObjData_LoadSLB(self.p_impl, path.encode('utf-8'))
        self.updateObjImpl()
        self.generateBbox()
        return ret
