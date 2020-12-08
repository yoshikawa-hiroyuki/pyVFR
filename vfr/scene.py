# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .gfxGroup import *
from .light import *

#----------------------------------------------------------------------
class Scene(GfxGroup):
    """
    シーンクラス
    Sceneクラスは、複数の子供のシーングラフノードとライティングノードを
    持つ事ができるノードで、シーングラフのルートとなるものです.
    """
    def __init__(self, name ='scene', suicide =False):
        GfxGroup.__init__(self, name, suicide)
        self._light = [Light(0, 'light0'), Light(1, 'light1'),
                       Light(2, 'light2'), Light(3, 'light3')]
        for l in self._light:
            l.addRef(self)
        self._light[0]._on = True
        return

    def __del__(self):
        GfxGroup.__del__(self)

    def destroy(self):
        del self._light[:]
        GfxGroup.destroy(self)
        return

    def getNodeById(self, id):
        """
        IDによるノード検索
        子供のノード群およびライティングノード群から、指定されたIDのノードを
        検索します．
        - id: 検索するノードID
        """
        if id == self._id: return self
        for c in self._children:
            ret = c.getNodeById(id)
            if ret: return ret
        for c in self._light:
            ret = c.getNodeById(id)
            if ret: return ret
        return None

    def getNodeByName(self, name):
        """
        名前によるノード検索
        子供のノード群およびライティングノード群から、指定された名前のノードを
        検索し、最初に見つかったノードを返します．
        - name: 検索するノードの名前
        """
        if self._name == name : return self
        for c in self._children:
            ret = c.getNodeByName(name)
            if ret: return ret
        for c in self._light:
            ret = c.getNodeByName(name)
            if ret: return ret
        return None

    def accumMatrix(self, tid, M):
        """
        幾何変換行列の累積演算
        指定されたIDを持つノードまでの幾何変換行列の累積演算を行い、
        Mに適用します.
        子供のノード群配下およびライティングノード群に指定されたIDを持つ
        ノードが存在しない場合はFalseを返します.
        - tid: ターゲットノードのID
        - M: 幾何変換行列
        """
        if self._id == tid:
            M1 = M * self._matrix
            M.m_v[0:] = M1.m_v[0:]
            return True
        for c in self._children:
            if c.getNodeById(tid):
                M1 = M * self._matrix
                if not c.accumMatrix(tid, M1): return False
                M.m_v[0:] = M1.m_v[0:]
                return True
        for c in self._light:
            if c.getNodeById(tid):
                M1 = M * self._matrix
                if not c.accumMatrix(tid, M1): return False
                M.m_v[0:] = M1.m_v[0:]
                return True
        return False

    def clearDispList(self):
        """
        OpenGLディスプレイリストの破棄
        再起的に全てのノードのOpenGLディスプレイリストを破棄します.
        """
        for c in self._children:
            c.clearDispList()
        for c in self._light:
            c.clearDispList()
        return

    def getLight(self, n):
        """
        ライティングノードの取得
        n番目のライティングノードを返します.
        - n: 取得するライトのインデックス番号
        """
        if n < 0 or n >= len(self._light): return None
        return self._light[n]

    def render(self):
        """
        シーンのレンダリング
        OpenGLによるシーンのレンダリングを行います.
        レンダリングパスは2パスで，1パス目に不透明ノードを，2パス目に
        半透明ノードをレンダリングします.
        """
        glPushName(0)
        self.applyMatrix()
        self.applyMaterial()

        # Traverse Lights
        for c in self._light:
            c.render()

        # Traverse Non-Transparent Children
        for c in self._children:
            c.render_(False)

        # Traverse Transparent Children
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for c in self._children:
            c.render_(True)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        self.unApplyMaterial()
        self.unApplyMatrix()
        glPopName()
        return

    def renderBbox(self):
        """
        バウンディングボックスのレンダリング
        """
        self.applyMatrix();
        glPushName(self._id)
        for c in self._light:
            c.renderBbox()
        for c in self._children:
            c.renderBbox()
        glPopName();
        self.unApplyMatrix()
        return
