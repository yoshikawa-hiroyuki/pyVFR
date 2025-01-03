#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, math, string
if not ".." in sys.path:
    sys.path = sys.path + [".."]


#----------------------------------------------------------------
# class ViewPoint
#----------------------------------------------------------------
from vfr import utilMath
import xform
import GfxView

class ViewPoint(object):
    def __init__(self, org =None):
        self.name = ''
        self.vT = utilMath.Vec3()
        self.vS = utilMath.Vec3((1.0, 1.0, 1.0))
        self.vC = utilMath.Vec3()
        self.mR = utilMath.Mat4()
        if org: self.setTo(org)

    def reset(self):
        self.vT[0:3] = [0.0]*3
        self.vS[0:3] = [1.0]*3
        self.vC[0:3] = [0.0]*3
        self.mR.Identity()

    def setTo(self, org):
        if isinstance(org, ViewPoint):
            self.vT[0:3] = org.vT[0:3]
            self.vS[0:3] = org.vS[0:3]
            self.vC[0:3] = org.vC[0:3]
            self.mR[0:16] = org.mR[0:16]
            return True
        if isinstance(org, GfxView.GfxView):
            self.vT[0:3] = org._T._matrix[12:15]
            self.vS[0] = org._S._matrix[0]
            self.vS[1] = org._S._matrix[5]
            self.vS[2] = org._S._matrix[10]
            self.vC[0:3] = org._C._matrix[12:15]
            self.mR[0:16] = org._R._matrix[0:16]
            return True
        return False

    def getRotQuat(self):
        rotQuat = utilMath.Quat4()
        m = self.mR
        EPS = 1.0e-3

        q0 = ( m[0] + m[5] + m[10] + 1.0) / 4.0
        q1 = ( m[0] - m[5] - m[10] + 1.0) / 4.0
        q2 = (-m[0] + m[5] - m[10] + 1.0) / 4.0
        q3 = (-m[0] - m[5] + m[10] + 1.0) / 4.0
        if q0 < 0.0: q0 = 0.0
        if q1 < 0.0: q1 = 0.0
        if q2 < 0.0: q2 = 0.0
        if q3 < 0.0: q3 = 0.0
        q0 = math.sqrt(q0)
        q1 = math.sqrt(q1)
        q2 = math.sqrt(q2)
        q3 = math.sqrt(q3)
        if q0 < EPS and q1 < EPS:
            q0 = 0.0
            q1 = 0.0
            q2 *= +1.0
            if m[6] + m[9] < 0.0:
                q3 *= -1.0
        elif q0 < EPS:
            q0 = 0.0
            q1 *= +1.0
            if m[1] + m[4] < 0.0:
                q2 *= -1.0
            if m[8] + m[2] < 0.0:
                q3 *= -1.0
        else:
            q0 *= +1.0
            if m[6] - m[9] < 0.0:
                q1 *= -1.0
            if m[8] - m[2] < 0.0:
                q2 *= -1.0
            if m[1] - m[4] < 0.0:
                q3 *= -1.0
        r = math.sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3)
        rotQuat.m_w = q0 / r
        rotQuat.m_i[0] = q1 / r
        rotQuat.m_i[1] = q2 / r
        rotQuat.m_i[2] = q3 / r
        return rotQuat


#----------------------------------------------------------------
# class ViewPointDlg
#----------------------------------------------------------------
import wx

class ViewPointDlg(wx.Dialog):
    def __init__(self, parent, refViewFrame):
        wx.Dialog.__init__(self, parent, -1, 'view point')
        self.p_viewFrame = refViewFrame

        sizerTop = wx.BoxSizer(orient=wx.VERTICAL)

        # standard view buttons
        iconDir = os.path.join(os.path.dirname(__file__), 'icon')
        sizerTop.Add(wx.StaticText(self, label='Standard view points'))
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_front.xpm'))
        self.m_pPzBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_back.xpm'))
        self.m_pMzBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_right.xpm'))
        self.m_pPxBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_left.xpm'))
        self.m_pMxBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_top.xpm'))
        self.m_pPyBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)
        pbm = wx.Bitmap(os.path.join(iconDir, 'view_bottom.xpm'))
        self.m_pMyBtn = wx.BitmapButton(self, -1, pbm, style=wx.BU_EXACTFIT)

        sizerH = wx.BoxSizer()
        sizerH.Add(self.m_pPzBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerH.Add(self.m_pMzBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerH.Add(self.m_pPxBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerH.Add(self.m_pMxBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerH.Add(self.m_pPyBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerH.Add(self.m_pMyBtn, proportion=1,
                   flag=wx.EXPAND|wx.ALL, border=3);
        sizerTop.Add(sizerH, flag=wx.EXPAND|wx.ALL, border=2)

        # registerd views
        sizerTop.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        sizerTop.Add(wx.StaticText(self, label='Registered view points'))

        # viewpoint name
        sizerH = wx.BoxSizer()
        self.m_pViewNameTxt = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        sizerH.Add(self.m_pViewNameTxt, flag=wx.EXPAND|wx.ALL,
                   proportion=1, border=3)
        self.m_pRegViewBtn = wx.Button(self, label='register')
        sizerH.Add(self.m_pRegViewBtn,
                   flag=wx.ALIGN_LEFT|wx.ALL, border=3)
        sizerTop.Add(sizerH, flag=wx.EXPAND|(wx.ALL & ~wx.TOP), border=5)

        # viewname list / restore, delete viewpoint
        sizerH = wx.BoxSizer()
        self.m_pViewNameLst = wx.ListBox(self, style=wx.LB_SINGLE|wx.LB_SORT)
        sizerH.Add(self.m_pViewNameLst, proportion=1,
                   flag=wx.EXPAND|wx.ALIGN_LEFT|(wx.ALL & ~wx.BOTTOM),border=3)
        sizerV = wx.BoxSizer(orient=wx.VERTICAL)
        sizerH.Add(sizerV, flag=wx.ALIGN_LEFT)
        self.m_pResViewBtn = wx.Button(self, label='restore')
        sizerV.Add(self.m_pResViewBtn, flag=wx.ALIGN_CENTER|wx.ALL, border=3)
        self.m_pDelViewBtn = wx.Button(self, label='delete')
        sizerV.Add(self.m_pDelViewBtn, flag=wx.ALIGN_CENTER|wx.ALL, border=3)
        sizerTop.Add(sizerH, flag=wx.EXPAND|(wx.ALL & ~wx.TOP), border=5)

        # close
        sizerTop.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        self.m_pCloseBtn = wx.Button(self, label='close')
        sizerTop.Add(self.m_pCloseBtn, flag=wx.ALIGN_RIGHT|wx.ALL,
                     border=3)

        self.SetSizer(sizerTop)
        sizerTop.Fit(self)
        self.Fit()

        # bind events
        self.Bind(wx.EVT_BUTTON, self.OnRightViewBtn, self.m_pPxBtn)
        self.Bind(wx.EVT_BUTTON, self.OnLeftViewBtn, self.m_pMxBtn)
        self.Bind(wx.EVT_BUTTON, self.OnTopViewBtn, self.m_pPyBtn)
        self.Bind(wx.EVT_BUTTON, self.OnBottomViewBtn, self.m_pMyBtn)
        self.Bind(wx.EVT_BUTTON, self.OnFrontViewBtn, self.m_pPzBtn)
        self.Bind(wx.EVT_BUTTON, self.OnBackViewBtn, self.m_pMzBtn)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnViewNameTxt, self.m_pViewNameTxt)
        self.Bind(wx.EVT_BUTTON, self.OnRegViewBtn, self.m_pRegViewBtn)
        self.Bind(wx.EVT_LISTBOX, self.OnViewNameLstClick,
                  self.m_pViewNameLst)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnViewNameLstDblClick,
                  self.m_pViewNameLst)
        self.Bind(wx.EVT_BUTTON, self.OnResViewBtn, self.m_pResViewBtn)
        self.Bind(wx.EVT_BUTTON, self.OnDelViewBtn, self.m_pDelViewBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCloseBtn, self.m_pCloseBtn)

        self.updateViewList()
        return

    def updateViewList(self):
        self.m_pViewNameLst.Clear()
        if not self.p_viewFrame: return False
        viewPointLst = self.p_viewFrame.viewPointLst
        for vpname in viewPointLst:
            self.m_pViewNameLst.Append(vpname)
        return True

    # event handlers
    def OnLeftViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        prot.roty(math.pi*0.5)
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnRightViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        prot.roty(-math.pi*0.5)
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnFrontViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnBackViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        prot.roty(math.pi)
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnTopViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        prot.rotx(math.pi*0.5)
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnBottomViewBtn(self, event):
        if not self.p_viewFrame: return
        pgv = self.p_viewFrame.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        prot.rotx(-math.pi*0.5)
        pgv.normalize()

        if GfxView.GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)
        else:
            prot.chkNotice()
        return

    def OnViewNameTxt(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameTxt.GetValue()
        if len(vpname) < 1: return

        xfm = self.p_viewFrame.getViewPoint(vpname)
        if xfm: # vpname already exists
            msg = 'View point named %s exists,\nAre you sure to override ?' % \
                vpname
            dlg = wx.MessageDialog(self._viewFrame,
                                   msg, 'set view point',
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_OK:
                return

        if not self.p_viewFrame.addViewPoint(vpname): return
        if not self.updateViewList(): return
        self.m_pViewNameLst.SetSelection(
            self.m_pViewNameLst.FindString(vpname))
        return

    def OnRegViewBtn(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameTxt.GetValue()
        if len(vpname) < 1:
            dlg = wx.MessageDialog(self.p_viewFrame,
                                   'View point with no name',
                                   'set view point failed',
                                   wx.OK|wx.CENTRE|wx.ICON_ERROR)
            dlg.ShowModal()
            return
        xfm = self.p_viewFrame.getViewPoint(vpname)
        if xfm: # vpname already exists
            msg = 'View point named %s exists,\nAre you sure to override ?' % \
                vpname
            dlg = wx.MessageDialog(self.p_viewFrame,
                                   msg, 'set view point',
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_OK:
                return

        if not self.p_viewFrame.addViewPoint(vpname): return
        if not self.updateViewList(): return
        self.m_pViewNameLst.SetSelection(
            self.m_pViewNameLst.FindString(vpname))
        return

    def OnViewNameLstClick(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameLst.GetStringSelection()
        if len(vpname) < 1: return
        self.m_pViewNameTxt.SetValue(vpname)
        return

    def OnViewNameLstDblClick(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameLst.GetStringSelection()
        if len(vpname) < 1: return
        self.m_pViewNameTxt.SetValue(vpname)

        if not self.p_viewFrame.updateViewPoint(vpname):
            return
        self.p_viewFrame.gfxView.drawArea.chkNotice()
        return

    def OnResViewBtn(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameLst.GetStringSelection()
        if len(vpname) < 1: return
        self.m_pViewNameTxt.SetValue(vpname)

        if not self.p_viewFrame.updateViewPoint(vpname):
            return
        self.p_viewFrame.gfxView.drawArea.chkNotice()
        return

    def OnDelViewBtn(self, event):
        if not self.p_viewFrame: return
        vpname = self.m_pViewNameLst.GetStringSelection()
        if len(vpname) < 1: return
        dlg = wx.MessageDialog(self.p_viewFrame,
                               'Are you sure to delete view point %s ?' % \
                               vpname, 'delete view point',
                               wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result != wx.ID_OK:
            return

        if self.p_viewFrame.delViewPoint(vpname):
            self.updateViewList()
        return

    def OnCloseBtn(self, event):
        self.Hide()
        
