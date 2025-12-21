#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Arena
#

""" Arena.
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from OpenGL.GL import *
from vfr import gfxGroup, gfxNode
from vfr import utilMath


#----------------------------------------------------------------------
def MatrixBbox(bbox, M):
    """幾何変換行列をバウンディングボックスに適用する
      bbox - utilMath.Vec3[2]. バウンディングボックス
      M - utilMath.Mat4. 幾何変換行列
      戻り値 -> utilMath.Vec3[2]
    """
    local = [utilMath.Vec3() for x in range(8)]
    local[0][0]=bbox[1][0]; local[0][1]=bbox[0][1]; local[0][2]=bbox[0][2]
    local[1][0]=bbox[1][0]; local[1][1]=bbox[1][1]; local[1][2]=bbox[0][2]
    local[2][0]=bbox[1][0]; local[2][1]=bbox[1][1]; local[2][2]=bbox[1][2]
    local[3][0]=bbox[1][0]; local[3][1]=bbox[0][1]; local[3][2]=bbox[1][2]
    local[4][0]=bbox[0][0]; local[4][1]=bbox[0][1]; local[4][2]=bbox[0][2]
    local[5][0]=bbox[0][0]; local[5][1]=bbox[0][1]; local[5][2]=bbox[1][2]
    local[6][0]=bbox[0][0]; local[6][1]=bbox[1][1]; local[6][2]=bbox[1][2]
    local[7][0]=bbox[0][0]; local[7][1]=bbox[1][1]; local[7][2]=bbox[0][2]

    box = [utilMath.Vec3(), utilMath.Vec3()]
    out = M * local[0]
    box[0][:] = out[:]; box[1][:] = out[:]
    for i in range(1, 8):
        out = M * local[i]
        if box[0][0] > out[0]: box[0][0] = out[0]
        if box[1][0] < out[0]: box[1][0] = out[0]
        if box[0][1] > out[1]: box[0][1] = out[1]
        if box[1][1] < out[1]: box[1][1] = out[1]
        if box[0][2] > out[2]: box[0][2] = out[2]
        if box[1][2] < out[2]: box[1][2] = out[2]
    return box


#----------------------------------------------------------------------
class Arena(gfxGroup.GfxGroup):
    """ Arenaクラス.
    """
    def __init__(self, **args):
        """ 初期設定.
        """
        gfxGroup.GfxGroup.__init__(self, **args)

        self.objRoot = gfxGroup.GfxGroup(name='OBJ_ROOT')
        self.volRoot = gfxGroup.GfxGroup(name='VOL_ROOT')
        self.addChild(self.objRoot)
        self.addChild(self.volRoot)
        
        self.selectedObj = None
        return

    def __del__ (self):
        """ 終了処理.
        """

    def reset(self):
        """ リセット. データおよびダイアログのクリア.
        """
        self.selectedObj = None
        self.objRoot.remAllChildren()
        self.volRoot.remAllChildren()
        return


    # select interface

    def setSelectedObj(self, obj):
        if obj is None:
            self.selectedObj = None
            return True
        found = False
        for i in range(self.getNumObject()):
            o = self.getObject(i)
            if obj == o:
                found = True
                break
        if not found:
            for i in range(self.getNumVolume()):
                v = self.getVolume(i)
                if obj == v:
                    found = True
                    break
        if not found:
            return False
        self.selectedObj = obj
        return True

    def getSelectedObj(self):
        return self.selectedObj
    
    
    # object interface
    
    def addObject(self, obj):
        """ Objectの追加.
          obj - Object. 追加するobject.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not self.objRoot.addChild(obj):
            return False
        return True

    def delObject(self, obj):
        """ Objectの削除.
          obj - Object. 削除するobject.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if obj == self.selectedObj:
            self.selectedObj = None
        if not self.objRoot.remChild(obj):
            return False
        return True

    def getObject(self, n):
        """ Objectの取得.
          n - int. index.
          戻り値 -> Object.
        """
        obj = self.objRoot.getChild(n)
        return obj

    def getNumObject(self):
        """ Object数の取得.
          戻り値 -> int. Objectの数.
        """
        return self.objRoot.getNumChildren()

    def getObjBbox(self, box, tgt):
        """ Object Bboxの取得.
          box - VolumeBox. 取得するBbox.
          tgt - target.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not tgt: return False
        tgtM = utilMath.Mat4()
        if not self.objRoot.accumMatrix(tgt.getID(), tgtM): return False

        nbox = MatrixBbox(tgt._bbox, tgtM)
        box[0][:] = nbox[0][:]; box[1][:] = nbox[1][:]
        return True


    # volume interface
    def addVolume(self, vol):
        """ Volumeの追加.
          vol - Volume. 追加するvolume.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if not self.volRoot.addChild(vol): return False
        return True

    def delVolume(self, vol):
        """ Volumeの削除.
          vol - Volume. 削除するvolume.
          戻り値 -> bool. 失敗したらFalseを返す.
        """
        if obj == self.selectedObj:
            self.selectedObj = None
        if not self.volRoot.remChild(vol): return False
        return True

    def getVolume(self, n):
        """ Volumeの取得.
          n - int. index.
          戻り値 -> Volume.
        """
        vol = self.volRoot.getChild(n)
        return vol

    def getNumVolume(self):
        """ Volume数の取得.
          戻り値 -> int. Volumeの数.
        """
        return self.volRoot.getNumChildren()


    def generateBbox(self):
        """ Bboxの生成.
        """
        self._bbox[0][:] = (0.0, 0.0, 0.0)
        self._bbox[1][:] = (0.0, 0.0, 0.0)
        cbox = [utilMath.Vec3(), utilMath.Vec3()]
        firstBox = True

        if self.objRoot.getNumChildren() > 0:
            self.objRoot.getMatrixBbox(cbox)
            self._bbox[0][:] = cbox[0][:]
            self._bbox[1][:] = cbox[1][:]
            firstBox = False

        if self.volRoot.getNumChildren() > 0:
            self.volRoot.getMatrixBbox(cbox)
            if firstBox:
                self._bbox[0][:] = cbox[0][:]
                self._bbox[1][:] = cbox[1][:]
                firstBox = False
            else:
                if self._bbox[0][0] > cbox[0][0]: self._bbox[0][0] = cbox[0][0]
                if self._bbox[1][0] < cbox[1][0]: self._bbox[1][0] = cbox[1][0]
                if self._bbox[0][1] > cbox[0][1]: self._bbox[0][1] = cbox[0][1]
                if self._bbox[1][1] < cbox[1][1]: self._bbox[1][1] = cbox[1][1]
                if self._bbox[0][2] > cbox[0][2]: self._bbox[0][2] = cbox[0][2]
                if self._bbox[1][2] < cbox[1][2]: self._bbox[1][2] = cbox[1][2]
        return


    def getSortedVolLst(self, MVM):
        """ ソートされたVolumeリストの取得.
          MVM - float
          戻り値 -> list.
        """
        if self.volRoot.getNumChildren() < 1:
            return []
        svrLst = []
        for pvn in self.volRoot._children:
            if pvn.getRenderMode() == gfxNode.RT_NONE: continue
            if not pvn.getFocus(): continue
            M = utilMath.Mat4()
            if not self.accumMatrix(pvn.getID(), M): continue
            M = MVM * M
            pbb = pvn.getBbox()
            c = (pbb[0] + pbb[1]) * 0.5
            c = M * c
            x = M * pbb[1]
            r = abs(x - c)
            svrLst += [(abs(c) - r, pvn)]
        if len(svrLst) < 1:
            return []
        return sorted(svrLst, lambda x, y : cmp(x[0],y[0]), reverse=True)


    def render_(self, transpMode):
        """
        override gfxGroup.GfxGroup.render_()
        """
        if self._renderMode == gfxNode.RT_NONE:
            return
        gfxGroup.GfxGroup.render_(self, transpMode)

        # call volume renderers
        if not transpMode: return
        if self.volRoot.getNumChildren() < 1: return
        
        modelMat = glGetFloatv(GL_MODELVIEW_MATRIX)
        MVM = utilMath.Mat4()
        MVM.m_v = modelMat.reshape(16)
        svrLst = self.getSortedVolLst(MVM)
        M = utilMath.Mat4()
        for d, pvn in svrLst:
            pvr = pvn.getVolumeRender()
            M.Identity()
            if self.accumMatrix(pvn.getID(), M) and pvr:
                pvr.DrawVolume(M)
        # done
        return
