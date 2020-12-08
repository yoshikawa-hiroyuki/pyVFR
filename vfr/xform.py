#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .utilMath import *


class XForm(object):
    """
    幾何変換クラス
    XFormクラスは，3次元の幾何変換を表現するクラスです．
    幾何変換は平行移動(T), 拡大縮小(S), 回転(HPR)および拡縮・回転中心(C)の
    各パラメータで表現します．
      _T: 平行移動量
      _S: スケーリングファクタ
      _C: 拡縮・回転中心座標
      _HPR: Head(Y軸周り回転), Pitch(X軸周り回転), Roll(Z軸周り回転)の各成分
    """
    __slots__=['_T', '_S', '_C', '_HPR']
    
    def __init__(self):
        self._T = Vec3()
        self._S = Vec3((1.0, 1.0, 1.0))
        self._C = Vec3()
        self._HPR = Vec3()

    def __str__(self):
        return 'XForm T=' + str(self._T) + ' S=' + str(self._S) + \
               ' C=' + str(self._C) + ' HPR=' + str(self._HPR)

    def getXFormMatrix(self):
        """
        幾何変換行列を返す
        各パラメータについて，対応する変換行列を以下のように合成したもの(M)を
        返します．
          [M] = [T][C][S][H][P][R][~C],  [~C]は[C]の逆行列
        """
        m = Mat4()
        m.Translate(self._T)
        m.Translate(self._C)
        m.RotY(Deg2Rad(self._HPR[0]))
        m.RotX(Deg2Rad(self._HPR[1]))
        m.RotZ(Deg2Rad(self._HPR[2]))
        m.Scale(self._S)
        m.Translate(- self._C)
        return m

    def updateXForm(self):
        """
        幾何変換の反映
        派生クラスにおいて幾何変換パラメータ変更時に実行する処理を実装します．
        """
        pass

    def resetXForm(self):
        """
        幾何変換の初期化
        """
        self._T[0:] = (0.0, 0.0, 0.0)
        self._C[0:] = (0.0, 0.0, 0.0)
        self._S[0:] = (1.0, 1.0, 1.0)
        self._HPR[0:] = (0.0, 0.0, 0.0)
        self.updateXForm()

    def setT(self, tv, upd =True):
        """
        平行移動量の設定
        - tv: 平行移動量
        - upd: Trueの時，updateXForm()をコールします
        """
        self._T[0:] = tv[0:]
        if upd: self.updateXForm()

    def setS(self, sv, upd =True):
        """
        スケーリングファクタの設定
        - sv: スケーリングファクタ
        - upd: Trueの時，updateXForm()をコールします
        """
        self._S[0:] = sv[0:]
        if upd: self.updateXForm()

    def setC(self, cv, upd =True):
        """
        拡大縮小・回転中心座標の設定
        - cv: 拡大縮小・回転中心座標
        - upd: Trueの時，updateXForm()をコールします
        """
        self._C[0:] = cv[0:]
        if upd: self.updateXForm()

    def setHPR(self, hpr, upd =True):
        """
        回転量の設定
        - hpr: 回転量成分
        - upd: Trueの時，updateXForm()をコールします
        """
        self._HPR[0:] = hpr[0:]
        if upd: self.updateXForm()

    # XML interface
    def importXMLNode(self, xnp):
        """
        XMLノードのパース
        - xnp: <xform>ノード
        """
        try:
            from xml.dom.minidom import parse
        except:
            return False
        if xnp.tagName != 'xform':
            return False

        self.resetXForm()
        for cur in xnp.childNodes:
            if cur.nodeType != cur.ELEMENT_NODE: continue
            if cur.tagName == 'translate':
                if cur.attributes.has_key('x'):
                    self._T[0] = float(cur.attributes['x'].value)
                if cur.attributes.has_key('y'):
                    self._T[1] = float(cur.attributes['y'].value)
                if cur.attributes.has_key('z'):
                    self._T[2] = float(cur.attributes['z'].value)
            elif cur.tagName == 'center':
                if cur.attributes.has_key('x'):
                    self._C[0] = float(cur.attributes['x'].value)
                if cur.attributes.has_key('y'):
                    self._C[1] = float(cur.attributes['y'].value)
                if cur.attributes.has_key('z'):
                    self._C[2] = float(cur.attributes['z'].value)
            elif cur.tagName == 'scale':
                if cur.attributes.has_key('x'):
                    self._S[0] = float(cur.attributes['x'].value)
                if cur.attributes.has_key('y'):
                    self._S[1] = float(cur.attributes['y'].value)
                if cur.attributes.has_key('z'):
                    self._S[2] = float(cur.attributes['z'].value)
            elif cur.tagName == 'hpr':
                if cur.attributes.has_key('h'):
                    self._HPR[0] = float(cur.attributes['h'].value)
                if cur.attributes.has_key('p'):
                    self._HPR[1] = float(cur.attributes['p'].value)
                if cur.attributes.has_key('r'):
                    self._HPR[2] = float(cur.attributes['r'].value)
            elif cur.tagName == 'rotate':
                if cur.attributes.has_key('x'):
                    self._HPR[1] = float(cur.attributes['x'].value)
                if cur.attributes.has_key('y'):
                    self._HPR[0] = float(cur.attributes['y'].value)
                if cur.attributes.has_key('z'):
                    self._HPR[2] = float(cur.attributes['z'].value)
        self.updateXForm()
        return True

    def exportXMLNode(self, file, ts =0):
        """
        XMLノードの出力
        指定されたファイルに<xform>ノード形式で出力します.
        - file: 出力先ファイル
        - ts: タブストップ
        """
        idts = ' ' * ts
        idts2 = idts + '  '
        try:
            file.write(idts + '<xform>\n')
        except:
            return False
        file.write(idts2 + '<translate x=\'%f\' y=\'%f\' z=\'%f\' />\n' %
                   (self._T[0], self._T[1], self._T[2]))
        file.write(idts2 + '<hpr h=\'%f\' p=\'%f\' r=\'%f\' />\n' %
                   (self._HPR[0], self._HPR[1], self._HPR[2]))
        file.write(idts2 + '<scale x=\'%f\' y=\'%f\' z=\'%f\' />\n' %
                   (self._S[0], self._S[1], self._S[2]))
        file.write(idts2 + '<center x=\'%f\' y=\'%f\' z=\'%f\' />\n' %
                   (self._C[0], self._C[1], self._C[2]))
        file.write(idts + '</xform>\n')
        return True

    def setTo(self, x):
        """
        代入
        """
        self._T[:] = x._T[:]
        self._S[:] = x._S[:]
        self._C[:] = x._C[:]
        self._HPR[:] = x._HPR[:]
        return


    def testXML(self, path):
        # export
        f = file(path, 'w')
        self.exportXMLNode(f)
        f.close()
        # import
        from xml.dom.minidom import parse
        doc = parse(path)
        xnp = doc.getElementsByTagName('xform')[0]
        self.importXMLNode(xnp)
        return
    
