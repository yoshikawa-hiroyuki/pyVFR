# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from gfxNode import *
from node import *


#----------------------------------------------------------------------
class GfxGroup(Group, GfxNode):
    """
    シーングラフ・グルーピングクラス
    GfxGroupクラスは、複数の子供のシーングラフノードを持つ事ができるノードで、
    シーングラフのブランチを構成するものです.
    """
    def __init__(self, name =Node._NONAME, suicide =False):
        Group.__init__(self, name, suicide)
        GfxNode.__init__(self, name, suicide)
        self._dlNodeType = False
        return

    def __del__(self):
        Group.__del__(self)
        GfxNode.__del__(self)
        return

    def destroy(self):
        self.remAllChildren()
        GfxNode.destroy(self)

    def render(self):
        """
        レンダリング
        OpenGLによるレンダリングを行います.
        """
        self.render_(False)
        self.render_(True)
        return

    def render_(self, transpMode):
        """
        レンダリング(半透明モード指定)
        半透明モードを指定して、全ての子供のノードのrender_()を呼び出します.
        - transpMode: 半透明モード
        """
        if self._renderMode == RT_NONE: return

        # push name for selection
        if self._pickable & PT_OBJECT :
            glPushName(self._id)

        # transformation matrix / material
        self.applyMatrix()
        self.applyMaterial()

        # rendering children
        for c in self._children:
            c.render_(transpMode)

        # un-apply material
        self.unApplyMaterial()

        # draw bbox
        if self._showBbox:
            if (transpMode and self._bboxColor[3] <= 0.999) or \
                   (not transpMode and self._bboxColor[3] > 0.999):
                if self._pickable & PT_OBJECT:
                    if not self._pickable & PT_BBOX:
                        glLoadName(0)
                self.drawBbox()

        # pop name for selection
        if self._pickable & PT_OBJECT:
            glPopName()

        # pop transformation matrix
        self.unApplyMatrix()
        return

    def renderBbox(self):
        """
        バウンディングボックスのレンダリング
        """
        self.applyMatrix();
        glPushName(self._id)
        for c in self._children:
            c.renderBbox()
        glPopName();
        self.unApplyMatrix()
        return

    def renderFeedBack(self, tgt):
        """
        フィードバックテスト用レンダリング
        フィードバックテストのためのレンダリングを行います.
        - tgt: フィードバックターゲットノードのID
        """
        if tgt == self._id:
            return
        if self.getNodeById(tgt) == None:
            return
        self.applyMatrix();
        for c in self._children:
            c.renderFeedBack(tgt)
        self.unApplyMatrix()
        return

    def addChild(self, node):
        """
        子ノードの追加
        指定されたノードを子供のノードに追加します.
        - node: 追加するノード
        """
        if not '_GfxNode__useDispList' in dir(node): return False
        if not Group.addChild(self, node): return False
        self.generateBbox()
        self.notice()
        return True

    def remChild(self, node):
        """
        子ノードの除外
        指定されたノードを子供のノードから除外します.
        - node: 除外されるノード
        """
        if not Group.remChild(self, node): return False
        self.generateBbox()
        self.notice()
        return True

    def remAllChildren(self):
        """
        全ての子ノードの除外
        全ての子供のノードを配下より除外します.
        """
        Group.remAllChildren(self)
        self.generateBbox()
        self.notice()
        return

    def accumMatrix(self, tid, M):
        """
        幾何変換行列の累積演算
        自分自身を含む、配下の指定されたIDを持つノードまでの幾何変換行列の
        累積演算を行い、Mに適用します.
        自分と，子供のノード群配下に指定されたIDを持つノードが存在しない場合は
        Falseを返します.
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
        return False

    def invalidateDispList(self):
        """
        OpenGLディスプレイリストの無効化
        再起的に全てのノードのOpenGLディスプレイリストを無効にします.
        """
        for c in self._children:
            c.invalidateDispList()
        return

    def clearDispList(self):
        """
        OpenGLディスプレイリストの破棄
        再起的に全てのノードのOpenGLディスプレイリストを破棄します.
        """
        for c in self._children:
            c.clearDispList()
        return

    def generateBbox(self):
        """
        バウンディングボックス再計算
        子ノードのバウンディングボックスから、自分のバウンディングボックスを
        再計算します.
        """
        if len(self._children) < 1: return
        cbox = [Vec3(), Vec3()]
        self._children[0].getMatrixBbox(cbox)
        self._bbox[0][0:] = cbox[0][0:]
        self._bbox[1][0:] = cbox[1][0:]

        for c in self._children:
            if c == self._children[0]: continue
            c.getMatrixBbox(cbox)
            if self._bbox[0][0] > cbox[0][0]: self._bbox[0][0] = cbox[0][0]
            if self._bbox[1][0] < cbox[1][0]: self._bbox[1][0] = cbox[1][0]
            if self._bbox[0][1] > cbox[0][1]: self._bbox[0][1] = cbox[0][1]
            if self._bbox[1][1] < cbox[1][1]: self._bbox[1][1] = cbox[1][1]
            if self._bbox[0][2] > cbox[0][2]: self._bbox[0][2] = cbox[0][2]
            if self._bbox[1][2] < cbox[1][2]: self._bbox[1][2] = cbox[1][2]
        return

    def notice(self, invalidateDL =True):
        """
        変更通知
        表示内容が変更されたことを親ノードに通知します.
        - invalidateDL: ディスプレイリスト無効化フラグ
        """
        self.generateBbox()
        Group.notice(self, invalidateDL)
        return

    def renderSolid(self):
        """
        ソリッドレンダリング
        ソリッドモードでOpenGLによるレンダリングを行います．
        """
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        for c in self._children:
            c.applyMatrix()
            c.applyMaterial()
            if c._renderMode & RT_NOLIGHT:
                glDisable(GL_LIGHTING)
            c.renderSolid()
            if c._renderMode & RT_NOLIGHT:
                glEnable(GL_LIGHTING)
            c.unApplyMaterial()
            c.unApplyMatrix()
        return

    def renderWire(self):
        """
        ワイヤーフレームレンダリング
        ワイヤーフレームモードでOpenGLによるレンダリングを行います．
        """
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDisable(GL_LIGHTING)
        for c in self._children:
            c.applyMatrix()
            c.applyMaterial()
            c.renderWire()
            c.unApplyMaterial()
            c.unApplyMatrix()
        glEnable(GL_LIGHTING)
        return

    def renderPoint(self):
        """
        ポイントレンダリング
        ポイントモードでOpenGLによるレンダリングを行います．
        """
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
        glDisable(GL_LIGHTING)
        for c in self._children:
            c.applyMatrix()
            c.applyMaterial()
            c.renderPoint()
            c.unApplyMaterial()
            c.unApplyMatrix()
        glEnable(GL_LIGHTING)
        return
