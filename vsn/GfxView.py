#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" GfxView.
"""

import sys, time, math
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *
from vfr import drawAreaWx
import Arena, xform
from ViewCamera import *
from FrontObj import *
import ViewPoint


class GfxView(object):
    """ GFX Viewクラス.
    """
    s_xformAnim = True
    s_xformAnimDuration = 0.5
    s_keyZoomInRatio = 1.1
    s_keyZoomInRatio2 = 2.0
    s_keyZoomOutRatio = 0.9
    s_keyZoomOutRatio2 = 0.5

    
    def __init__(self, parent):
        """ 初期設定.
         それぞれ以下のGfxGroupを表します.
         T : 平行移動
         C : 回転・スケーリング中心
         R : 回転
         S : スケーリング
         IC : Cの逆変換
         ROOT : シーンのルート(Arena)
         parent - wx.Window. 親widget
        selected - 選択中のオブジェクト
        _xformSimpleRendering: 幾何変換時の簡易レンダリングモード
        _xforming: 幾何変換実行中フラグ
        """
        self.drawArea = drawAreaWx.DrawAreaWx(parent)
        self.parent = parent

        self.camera = ViewCamera(suicide=True)
        self.camera._frustum._eye[2] = 15.0
        self.camera._frustum._dist = 15.0
        self.camera._antiAlias = True
        self.drawArea.setCamera(self.camera)

        self.scene = scene.Scene(suicide=True)
        self.camera.setScene(self.scene)

        self._T = gfxGroup.GfxGroup(name='T', suicide=True)
        self.scene.addChild(self._T)
        self._C = gfxGroup.GfxGroup(name='C', suicide=True)
        self._T.addChild(self._C)
        self._R = gfxGroup.GfxGroup(name='R', suicide=True)
        self._C.addChild(self._R)
        self._S = gfxGroup.GfxGroup(name='S', suicide=True)
        self._R.addChild(self._S)
        self._IC = gfxGroup.GfxGroup(name='IC', suicide=True)
        self._S.addChild(self._IC)
        self.root = Arena.Arena(name='ROOT', suicide=True)
        self._IC.addChild(self.root)

        self.faxis = FrontAxis(suicide=True)
        self.camera.addToFront(self.faxis)

        self.centPos = gfxNode.GfxNode(name='CenterPos', suicide=True)
        self.centPos.alcData(nV=1, nC=1)
        self.centPos.setColor(0, (1.0, 1.0, 0.0))
        self.centPos.setRenderMode(gfxNode.RT_POINT)
        self.centPos.setPointSymbol(gfxNode.SYM_PLUS)
        self._IC.addChild(self.centPos)

        self._xformSimpleRendering = True
        self._xforming = False

        self.setupActions()
        return

    def __del__(self):
        """ 終了処理.
        """
        self.camera.destroy()
        del self.parent
        del self.drawArea
        del self.camera
        del self.scene
        del self._T, self._C, self._R, self._S, self._IC, self.root
        del self.centPos
        return

    def getArena(self):
        return self.root
        
    @staticmethod
    def GetTime():
        """ 時刻の取得.
          戻り値 -> float. time値.
        """
        return time.time()
        
    def getXformSimpleRendering(self):
        """ 幾何変換時の簡易レンダリングモードの取得.
          戻り値 -> bool. 幾何変換時の簡易レンダリングモードの値.
        """
        return self._xformSimpleRendering

    def setXformSimpleRendering(self, mode):
        """ xformSimpleRenderingの設定.
          mode - bool. simple rendering in transformationの設定値.
        """
        self._xformSimpleRendering = mode

    def getXforming(self):
        """ 幾何変換中フラグの取得.
          戻り値 -> bool. 幾何変換中フラグの値.
        """
        return self._xforming

    def setXforming(self, mode):
        """ 幾何変換中フラグのの設定.
          mode - bool. 幾何変換中フラグの設定値.
        """
        if self._xforming == mode: return
        self._xforming = mode
        self.scene.notice()
        return        

    def addToRoot(self, node, is_volume=False):
        """ rootへのnodeの追加.
          node - Node.追加するnode
          戻り値 -> bool. 失敗ならFalseを返す.
        """
        if is_volume:
            return self.root.addVolume(node)
        else:
            return self.root.addObject(node)

    def remFromRoot(self, node):
        """ rootからのnodeの削除.
          node - Node. 削除するnode.
          戻り値 -> bool. 失敗ならFalseを返す.
        """
        if self.root.delObject(node):
            return True
        elif self.root.delVolume(node):
            return True
        else:
            return False

    def sceneGraphUpdated(self):
        """ Scene graphの更新.
        """
        self.faxis.setRotMatrix(self._R._matrix)
        return

    def normalize(self, target =None, withCenter =True):
        """ Normalizeの実行.
          target - Node. 操作対象.
          withCenter - bool. True:Cへの操作を伴う, False:伴わない.
        """
        self._T.identity()
        self._S.identity()
        if withCenter:
            self._C.identity()
            self._IC.identity()
            self.centPos.identity()
        self.root.identity()
        if target:
            M = utilMath.Mat4()
            self.root.accumMatrix(target._id, M)
            bb = target._bbox
            sbb = Arena.MatrixBbox(bb, M)
        else:
            sbb = [utilMath.Vec3(), utilMath.Vec3()]
            self.root.getMatrixBbox(sbb)
        bbLen = (sbb[1] - sbb[0]).__abs__()

        # scale
        if bbLen > 1e-8:
            vw = self.camera._frustum._halfW * 2
            self._S.scale(vw / bbLen)
        # translate
        bbC = (sbb[1] + sbb[0]) * 0.5
        xbbC = utilMath.Vec3(bbC)
        X = utilMath.Mat4()
        if self._C.accumMatrix(self.root._id, X):
            xbbC[0:] = (X * bbC)[0:]
        self._T.trans(xbbC * (-1.0))

        # center
        if withCenter:
            self.setCenter(bbC)

        self.sceneGraphUpdated()
        return

    def sweepZoom(self, p0, p1):
        """ Sweep zoomの実行.
          p0 - Point.
          p1 - Point.
          戻り値 - bool. 失敗したらFalseを返す.
        """
        pp = gfxNode.Point2((p0.x + p1.x) / 2, (p0.y + p1.y) / 2)
        vpSize = self.drawArea.getSize()
        m0 = gfxNode.Point2(vpSize.x / 2, vpSize.y / 2)

        # translate
        tid = self.scene.getID()
        (objp1, objp2) = (utilMath.Vec3(), utilMath.Vec3())
        if not self.drawArea.getObjCoord(tid, m0, objp1): return False
        if not self.drawArea.getObjCoord(tid, pp, objp2): return False
        tv = objp1 - objp2
        self._T.trans(tv)

        # center
        self.setCenterP(m0)

        # zoom
        ppLen = abs(utilMath.Vec3((p1.x - p0.x, p1.y - p0.y, 0.0)))
        vpLen = abs(utilMath.Vec3((vpSize.x, vpSize.y, 0.0)))
        if ppLen > 1e-6: self._S.scale(vpLen / ppLen)

        self.sceneGraphUpdated()
        return True

    def setCenter(self, cp):
        """ 中心の設定.
         GfxViewの中心のみを移動します. ３次元座標で中心を指定します.
          cp - Vec3. 中心の座標.
        scene graph tree: scene->T->C->R->S->C~->root
         [X] := [T][C][R][S][C~]
         [Tnew] = [X]([Cnew][R][S][Cnew~])~
        """
        (X, Y) = (utilMath.Mat4(), utilMath.Mat4())
        if not self.scene.accumMatrix(self.root.getID(), X):
            return
        cv = utilMath.Vec3(cp)

        self._T.identity()
        self._C.identity()
        self._IC.identity()

        self._C.trans(cv)
        self._IC.trans(cv * (-1.0))

        if not self._C.accumMatrix(self.root.getID(), Y):
            return
        iY = Y.inverse()
        Y = X * iY   # [Tnew]
        cv0 = Y * utilMath.Vec3()
        self._T.trans(cv0)

        self.centPos.identity()
        self.centPos.trans(cv)

        self.sceneGraphUpdated()
        return

    def getCenter(self):
        """ 中心の位置を取得.
          戻り値 -> Point2. 中心の座標.
        """
        mC = self.centPos.getMatrix()
        cp = [mC[12], mC[13], mC[14]]
        return cp

    def setCenterP(self, cp):
        """ 中心の設定.
         GfxViewの中心のみを移動します. ウィンドウ座標で中心を指定します.
          cp - Point2. 中心の座標. 
        """
        o = utilMath.Vec3()
        cp0 = gfxNode.Point2()
        if not self.drawArea.getWinCoord(self.centPos.getID(), o, cp0):
            return
        cp0.y = self.drawArea.getSize().y - cp0.y
        cd = cp - cp0
        self.drawArea.translateNode(self.centPos, cp0, cd)

        oc = self.getCenter()
        self.setCenter(oc)
        return
    
    def getComposedMatrix(self, tid =0):
        """ 変換のために組み立てられたMatrixの取得.
          tid - int. sceneのid
          戻り値 -> Matrix. Matrix値.
        """
        rM = utilMath.Mat4()
        if self.camera is None or self.drawArea is None : return rM

        asp = self.drawArea._viewport[2] / self.drawArea._viewport[3]
        rM = self.drawArea.getViewportMatrix() * self.camera.getProjMatrix(asp)

        if tid == 0:
            self.camera.accumMatrix(self.scene._id, rM)
        else:
            self.camera.accumMatrix(tid, rM)
        return rM

    def setViewPoint(self, xfm):
        """ ViewPointの設定.
          xfm - ViewPoint.
        """
        self._T.identity(); self._T.trans(xfm.vT)
        self._S.identity(); self._S.scale(xfm.vS)
        self._C.identity(); self._C.trans(xfm.vC)
        self._IC.identity(); self._IC.trans(xfm.vC * (-1.0))
        self._R._matrix[0:16] = xfm.mR[0:16]
        self.centPos.identity(); self.centPos.trans(xfm.vC)
        self.sceneGraphUpdated()
        return

    def getViewPoint(self):
        """ ViewPointの取得.
          戻り値 -> ViewPoint.
        """
        vp = ViewPoint.ViewPoint()
        vp.setTo(self)
        return vp

    def setViewXForm(self, xfm):
        """ XFormの設定.
          xfm - ViewPoint.
        """
        if not GfxView.s_xformAnim or GfxView.s_xformAnimDuration <= 0.0:
            self.setViewPoint(xfm)
            return

        wxfm = ViewPoint.ViewPoint()
        xfm0 = self.getViewPoint()
        rQ0 = xfm0.getRotQuat().unit()
        rQ = xfm.getRotQuat().unit()
        wT = xfm.vT - xfm0.vT
        wC = xfm.vC - xfm0.vC
        wS = xfm.vS - xfm0.vS

        totalTime = GfxView.s_xformAnimDuration
        startTime = GfxView.GetTime()
        elapsTime = 0.0
        self.setXforming(True)

        while elapsTime < totalTime:
            dt = elapsTime / totalTime
            wQ = utilMath.QuatSlerp(rQ0, rQ, dt)

            wxfm.mR = wQ.rotMat()
            wxfm.vT = xfm0.vT + (wT * dt)
            wxfm.vC = xfm0.vC + (wC * dt)
            wxfm.vS = xfm0.vS + (wS * dt)
            self.setViewPoint(wxfm)
            self.drawArea.chkNotice()
            try:
                app = self.parent.getApp()
                app.Yield()
            except:
                pass # may cause wxYield called recursively
            elapsTime = GfxView.GetTime() - startTime

        # the last xform
        self.setViewPoint(xfm)
        self.drawArea.chkNotice()

        self.setXforming(False)
        self.drawArea.chkNotice()
        return

    def setPerspective(self, pm):
        """ Perspectiveの設定.
          pm - bool. Perspectiveのモード.
               True:on, False:off.
        """
        if pm: proj = gfxNode.PR_PERSPECTIVE
        else: proj = gfxNode.PR_ORTHOGONAL
        self.camera.setProjection(proj)
        self.camera.chkNotice()
        return

    def setShowFrontAxis(self, mode):
        """ FrontAxisの表示の設定.
          mode - bool. True:表示する, False:しない.
        """
        if not self.faxis: return
        if mode:
            self.faxis.setRenderMode(gfxNode.RT_SMOOTH)
        else:
            self.faxis.setRenderMode(gfxNode.RT_NONE)
        self.faxis.chkNotice()
        return

    def getShowFrontAxis(self):
        """ FrontAxisの表示モードの取得.
          戻り値 - bool. True:表示, False:非表示.
        """
        if not self.faxis: return False
        if self.faxis._renderMode == gfxNode.RT_NONE:
            return False
        else:
            return True

    def setShowCenterPos(self, mode):
        """ 中心の表示の設定.
          mode - bool. True:表示する, False:しない.
        """
        if not self.centPos: return
        if mode:
            self.centPos.setRenderMode(gfxNode.RT_POINT)
        else:
            self.centPos.setRenderMode(gfxNode.RT_NONE)
        self.centPos.chkNotice()
        return

    def getShowCenterPos(self):
        """ 中心の表示モードの取得.
          戻り値 - bool. True:表示, False:非表示.
        """
        if not self.centPos: return False
        if self.centPos._renderMode == gfxNode.RT_NONE:
            return False
        else:
            return True
    
    def setupActions(self):
        """ 操作の設定.
        """
        import GfxActs

        # KeyIn
        KeyIn = self.drawArea.getEvent(events.EVT_KeyIn)
        KeyIn.regist(GfxActs.GfxAct_KeyIn(gv=self))

        # Click : Focus
        Click = self.drawArea.getEvent(events.EVT_Click)
        Click.regist(GfxActs.GfxAct_Click(gv=self))

        # Shift+Dragging : Translation
        transAct = GfxActs.GfxAct_TransScene(gv=self)
        self.drawArea.getEvent(events.EVT_SDrag).regist(transAct)
        self.drawArea.getEvent(events.EVT_SDragStart).regist(transAct)
        self.drawArea.getEvent(events.EVT_SDragEnd).regist(transAct)

        # Dragging : Rotation
        rotAct = GfxActs.GfxAct_RotScene(gv=self)
        self.drawArea.getEvent(events.EVT_Drag).regist(rotAct)
        self.drawArea.getEvent(events.EVT_DragStart).regist(rotAct)
        self.drawArea.getEvent(events.EVT_DragEnd).regist(rotAct)
        
        # Cntl+Dragging : Scaling
        scaleAct = GfxActs.GfxAct_ScaleScene(gv=self)
        self.drawArea.getEvent(events.EVT_CDrag).regist(scaleAct)
        self.drawArea.getEvent(events.EVT_CDragStart).regist(scaleAct)
        self.drawArea.getEvent(events.EVT_CDragEnd).regist(scaleAct)

        # Wheel : Scaling
        Wheel = self.drawArea.getEvent(events.EVT_Wheel)
        Wheel.regist(GfxActs.GfxAct_WheelScene(gv=self))

        # Cntl+Shift+{Click,Dragging} : Selection
        selectAct = GfxActs.GfxAct_Selection(gv=self)
        startRbAct = GfxActs.GfxAct_StartRBox(gv=self)
        drawRbAct = defaultActions.DrawRBoxAction()
        self.drawArea.getEvent(events.EVT_SCClick).regist(selectAct)
        self.drawArea.getEvent(events.EVT_SCDragStart).regist(startRbAct)
        self.drawArea.getEvent(events.EVT_SCDrag).regist(drawRbAct)
        self.drawArea.getEvent(events.EVT_SCDragEnd).regist(selectAct)

        # Shift+MDragging : SweepZoom
        startZoomAct = GfxActs.GfxAct_StartRBox(gv=self, lineWidth=1.5,
                                                lineType=gfxNode.ST_DASH)
        endZoomAct = GfxActs.GfxAct_SweepZoom(gv=self)
        self.drawArea.getEvent(events.EVT_MSDragStart).regist(startZoomAct)
        self.drawArea.getEvent(events.EVT_MSDrag).regist(drawRbAct)
        self.drawArea.getEvent(events.EVT_MSDragEnd).regist(endZoomAct)

        return
