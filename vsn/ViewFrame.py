#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
View Frame implementation
"""

import sys, os, math
import wx
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from GfxView import GfxView
from GfxActs import *
import ViewPoint
import ObjSelectDlg
import ObjPropDlg

# Menu Ids
(ViewFrameMenu_File_Quit,
 
 ViewFrameMenu_View_Normalize,
 ViewFrameMenu_View_NormalizeScene,
 ViewFrameMenu_View_SetViewPoint,
 ViewFrameMenu_View_Perspective,
 ViewFrameMenu_View_CenterShow,
 ViewFrameMenu_View_FrAxisShow,
 ViewFrameMenu_View_SetBgColor,

 ViewFrameMenu_Obj_Selection,
 
 ViewFrameMenu_Help_About) = range(1100, 1100 + 10)

(ViewFrameTooBar_NormView,
 ViewFrameTooBar_ProjPers,
 ViewFrameTooBar_ProjOrtho,
 ViewFrameTooBar_Front,
 ViewFrameTooBar_Back,
 ViewFrameTooBar_Right,
 ViewFrameTooBar_Left,
 ViewFrameTooBar_Top,
 ViewFrameTooBar_Bottom) = range(1150, 1150 + 9)


class ViewFrame(wx.Frame):
    """ View Frameクラス.
    """
    FRAME_DEFAULT_VPNAME = "( viewpoint0 )"


    def __init__(self, parent, ID=-1, title='ViewFrame', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE,
                 name='frame'):
        """ 初期設定.
          parent - wx.Window. parent window.
          ID - int. id.
          title - String. 表題.
          pos - Point. position.
          size - Size. size.
          style - long. style.
          name - String. name.
        """
        # view point dialog
        self.viewPointLst = {}
        self.pViewPointDlg = None

        # visObj properties dialog
        self.pObjPropDlg = None

        wx.Frame.__init__(self, parent, ID, title, pos, size, style, name)
        self.parent = parent

        self.app = None
        self.gfxView = GfxView(self)

        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(self.gfxView.drawArea._canvas, 1, wx.EXPAND)
        self.SetSizer(topsizer)
        topsizer.Layout()
        
        # menu bar, tool bar
        self.setupMenuBar()
        self.setupToolBar()

        return

    
    def __del__(self):
        """ 終了処理.
        """
        if self.gfxView: del self.gfxView
        return

    
    def isViewFrame(self):
        return True
    

    def setApp(self, app):
        """ App設定
          app - App.
        """
        self.app = app
        return

    def getApp(self):
        return self.app


    def getArena(self):
        return self.gfxView.getArena()
    
    
    def setupMenuBar(self):
        """ Menu barとmenuの作成.
        """
        # 'File' menu
        fileMenu = wx.Menu()
        fileMenu.Append(ViewFrameMenu_File_Quit,
                        "Quit\tCTRL+Q",
                        "Quit vsn view")

        # 'View' menu
        viewMenu = wx.Menu()
        viewMenu.Append(ViewFrameMenu_View_Normalize,
                        "Fit to Selected Objects\tSPACE",
                        "Fit Viewport to Selected Objects")
        viewMenu.Append(ViewFrameMenu_View_NormalizeScene,
                        "Fit to Scene\tSHIFT+SPACE",
                        "Fit Viewport to Scene")
        viewMenu.Append(ViewFrameMenu_View_SetViewPoint,
                        "Set View Points ...", "Set View Points")
        viewMenu.Append(ViewFrameMenu_View_Perspective,
                        "Perspective", "Perspective projection",
                        wx.ITEM_CHECK)
        viewMenu.AppendSeparator()
        viewMenu.Append(ViewFrameMenu_View_FrAxisShow,
                        "Show Coordinate Axis",
                        "Show/Hide Coordinate Axis glyph in front layer", True)
        viewMenu.Append(ViewFrameMenu_View_CenterShow,
                        "Show Center Cross\tCTRL+C",
                        "Show/Hide glyph of Rot|Scale Center", True)
        viewMenu.AppendSeparator()
        viewMenu.Append(ViewFrameMenu_View_SetBgColor,
                        "Background Color ...",
                        "Set Background Color of Graphics drawing area")

        # 'Obj' menu
        objMenu = wx.Menu()
        objMenu.Append(ViewFrameMenu_Obj_Selection,
                        "Select VisObj ...",
                        "Select a VisObj")

        # 'Help' menu
        helpMenu = wx.Menu()
        helpMenu.Append(ViewFrameMenu_Help_About,
                        "About vsn ...", "Show vsn version")

        # menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(viewMenu, "View")
        menuBar.Append(objMenu, "Obj")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        # event
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # update UI
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu)

        return


    def setupToolBar(self):
        """ ToolBarのセットアップ.
          戻り値 -> bool.
        """
        ptb = self.GetToolBar()
        if ptb: return True
        ptb = self.CreateToolBar()
        if not ptb: return False

        (TB_NormView, TB_ProjPers, TB_ProjOrtho,
         TB_Front, TB_Back, TB_Right, TB_Left, TB_Top, TB_Bottom) = range(9)
        iconDir = os.path.join(os.path.dirname(__file__), 'icon')
        tbBmps = [
            wx.Bitmap(os.path.join(iconDir, 'view_norm.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'proj_pers.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'proj_ortho.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_front.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_back.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_right.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_left.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_top.xpm')),
            wx.Bitmap(os.path.join(iconDir, 'view_bottom.xpm'))
            ]
        ptb.SetToolBitmapSize(tbBmps[0].GetSize())

        ptb.AddTool(ViewFrameTooBar_ProjPers, 'perspective',
                    tbBmps[TB_ProjPers], tbBmps[TB_ProjPers], wx.ITEM_NORMAL,
                    'perspective projection')
        ptb.AddTool(ViewFrameTooBar_ProjOrtho, 'parallel',
                    tbBmps[TB_ProjOrtho], tbBmps[TB_ProjOrtho], wx.ITEM_NORMAL,
                    'parallel projection')
        ptb.AddSeparator()
        ptb.AddTool(ViewFrameTooBar_NormView, 'normalize',
                    tbBmps[TB_NormView], tbBmps[TB_NormView], wx.ITEM_NORMAL,
                    'normalize(fit) view')
        ptb.AddSeparator()
        ptb.AddTool(ViewFrameTooBar_Front, 'front',
                    tbBmps[TB_Front], tbBmps[TB_Front], wx.ITEM_NORMAL,
                    'view from +Z')
        ptb.AddTool(ViewFrameTooBar_Back, 'back',
                    tbBmps[TB_Back], tbBmps[TB_Back], wx.ITEM_NORMAL,
                    'view from -Z')
        ptb.AddTool(ViewFrameTooBar_Right, 'right',
                    tbBmps[TB_Right], tbBmps[TB_Right], wx.ITEM_NORMAL,
                    'view from +X')
        ptb.AddTool(ViewFrameTooBar_Left, 'left',
                    tbBmps[TB_Left], tbBmps[TB_Left], wx.ITEM_NORMAL,
                    'view from -X')
        ptb.AddTool(ViewFrameTooBar_Top, 'top',
                    tbBmps[TB_Top], tbBmps[TB_Top], wx.ITEM_NORMAL,
                    'view from +Y')
        ptb.AddTool(ViewFrameTooBar_Bottom, 'bottom',
                    tbBmps[TB_Bottom], tbBmps[TB_Bottom], wx.ITEM_NORMAL,
                    'view from -Y')
        ptb.Realize()

        self.Bind(wx.EVT_TOOL, self.OnToolBar_Projection,
                  id=ViewFrameTooBar_ProjPers)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_Projection,
                  id=ViewFrameTooBar_ProjOrtho)
        
        self.Bind(wx.EVT_TOOL, self.OnToolBar_Normalize,
                  id=ViewFrameTooBar_NormView)

        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Front)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Back)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Right)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Left)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Top)
        self.Bind(wx.EVT_TOOL, self.OnToolBar_ViewDirs,
                  id=ViewFrameTooBar_Bottom)

        return True
        

    def getViewPoint(self, vpname):
        """ view pointの取得.
          vpname - String. 取得するview point名.
          戻り値 -> viewPoint.
        """
        try:
            vp = self.viewPointLst[vpname]
            return vp
        except:
            pass
        return None

    def addViewPoint(self, vpname):
        """ view pointの追加.
          vpname - String. 追加するview point名.
          戻り値 -> bool.
        """
        if not vpname or len(vpname) < 1: return False
        xfm = self.gfxView.getViewPoint()
        xfm.name = vpname
        self.viewPointLst[vpname] = xfm
        return self.updateViewPoint(vpname, xanim=False)

    def delViewPoint(self, vpname):
        """ view pointの削除.
          vpname - String. 削除するview point名.
          戻り値 -> bool.
        """
        try:
            self.viewPointLst.pop(vpname)
            return True
        except:
            pass
        return False

    def updateViewPoint(self, vpname, xanim =True):
        """ view pointの更新.
          vpname - String. view point名.
          xanim - bool. アニメーションモードのon/off.
          戻り値 -> bool.
        """
        try:
            xfm = self.viewPointLst[vpname]
            if xanim:
                self.gfxView.setViewXForm(xfm)
            else:
                self.gfxView.setViewPoint(xfm)
            return True
        except:
            pass
        return False
        

    def reset(self):
        # reset view points
        self.viewPointLst = {}
        if self.pViewPointDlg:
            self.pViewPointDlg.Hide()

        # reset visObj properties dialog
        if self.pObjPropDlg:
            self.pObjPropDlg.Hide()

        # reset bg color
        self.setBgColor([0, 0, 0])

        return


    def setBgColor(self, color):
        """ background colorの設定.
          color - tuple. background color.
        """
        self.gfxView.camera.setBgColor(color)
        self.gfxView.drawArea.chkNotice()
        return

    def getBgColor(self):
        """ background colorの取得.
          戻り値 -> tuple. background color.
        """
        return tuple(self.gfxView.camera._bgColor)


    def refresh(self, reSelObj =False):
        """ refresh.
        """
        # GfxView part
        self.gfxView.drawArea.chkNotice()

        self.Refresh()
        return


    def OnMenu(self, event):
        eid = event.GetId()
        if eid == ViewFrameMenu_File_Quit:
            self.OnMenuFile_Quit(event)
        elif eid == ViewFrameMenu_View_Normalize:
            self.OnMenuView_Normalize(event)
        elif eid == ViewFrameMenu_View_NormalizeScene:
            self.OnMenuView_NormalizeScene(event)
        elif eid == ViewFrameMenu_View_SetViewPoint:
            self.OnMenuView_SetViewPoint(event)
        elif eid == ViewFrameMenu_View_Perspective:
            self.OnMenuView_Perspective(event)
        elif eid == ViewFrameMenu_View_FrAxisShow:
            self.OnMenuView_FrAxisShow(event)
        elif eid == ViewFrameMenu_View_CenterShow:
            self.OnMenuView_CenterShow(event)
        elif eid == ViewFrameMenu_View_SetBgColor:
            self.OnMenuView_SetBgColor(event)
        elif eid == ViewFrameMenu_Obj_Selection:
            self.OnMenuObj_Selection(event)
        elif eid == ViewFrameMenu_Help_About:
            self.OnMenuHelp_About(event)
        return

    def OnMenuFile_Quit(self, event):
        """ Quitメニューのイベント.
         event - wx.MenuEvent.
        """
        #self.Close(True)
        self.Destroy()
        return

    def OnMenuView_Normalize(self, event):
        """ Fit to Selected Objectsメニューのイベント.
          event - wx.MenuEvent.
        """
        pTgt = None

        if not GfxView.s_xformAnim or GfxView.s_xformAnimDuration <= 0.0:
            self.gfxView.normalize(pTgt)
            self.gfxView.drawArea.chkNotice()
            return
        vp0 = self.gfxView.getViewPoint()
        self.gfxView.normalize(pTgt)
        vp1 = self.gfxView.getViewPoint()
        self.gfxView.setViewPoint(vp0)
        self.gfxView.setViewXForm(vp1)
        self.gfxView.sceneGraphUpdated()
        return


    def OnMenuView_NormalizeScene(self, event):
        """ Fit to Sceneメニューのイベント.
          event - wx.MenuEvent.
        """
        if not GfxView.s_xformAnim or GfxView.s_xformAnimDuration <= 0.0:
            self.gfxView.normalize()
            self.gfxView.drawArea.chkNotice()
            return
        vp0 = self.gfxView.getViewPoint()
        self.gfxView.normalize()
        vp1 = self.gfxView.getViewPoint()
        self.gfxView.setViewPoint(vp0)
        self.gfxView.setViewXForm(vp1)
        self.gfxView.sceneGraphUpdated()
        return


    def OnMenuView_SetViewPoint(self, event):
        """ Set View Pointsメニューのイベント.
          event - wx.MenuEvent.
        """
        if not self.pViewPointDlg:
            self.pViewPointDlg = ViewPoint.ViewPointDlg(self, self)
        self.pViewPointDlg.Show(True)
        return
    

    def OnUpdateMenu(self, event):
        eid = event.GetId()
        if eid == ViewFrameMenu_View_Perspective:
            self.OnUpdateMenuView_Perspective(event)
        elif eid == ViewFrameMenu_View_FrAxisShow:
            self.OnUpdateMenuView_FrAxisShow(event)
        elif eid == ViewFrameMenu_View_CenterShow:
            self.OnUpdateMenuView_CenterShow(event)
        return

    def OnMenuView_Perspective(self, event):
        """ Perspectiveメニューのイベント.
          event - wx.MenuEvent.
        """
        pm = event.IsChecked()
        self.gfxView.setPerspective(pm)

    def OnUpdateMenuView_Perspective(self, event):
        """ PerspectiveのUPDATE UIイベント.
          event - wx.UpdateUIEvent.
        """
        pm = self.gfxView.camera.getProjection()
        if pm == gfxNode.PR_PERSPECTIVE:
            event.Check(True)
        else:
            event.Check(False)
        return

    def OnMenuView_ShowToolBar(self, event):
        """ Show Toolbarメニューのイベント.
          event - wx.MenuEvent.
        """
        mode = event.IsChecked()
        ptb = self.GetToolBar()
        if mode:
            if ptb: return
            self.setupToolBar()
        else:
            if ptb:
                self.SetToolBar(None)
                ptb.Destroy()
        self.Refresh()
        return

    def OnUpdateMenuView_ShowToolBar(self, event):
        """ Show ToolbarのUPDATE UIイベント.
          event - wx.UpdateUIEvent.
        """
        ptb = self.GetToolBar()
        event.Check(ptb != None)
        return

    def OnMenuView_FrAxisShow(self, event):
        self.gfxView.setShowFrontAxis(event.IsChecked())
        """ Show Coordinate Axisメニューのイベント.
          event - wx.MenuEvent.
        """
        return

    def OnUpdateMenuView_FrAxisShow(self, event):
        """ Show Coordinate AxisのUPDATE UIイベント.
          event - wx.UpdateUIEvent.
        """
        event.Check(self.gfxView.getShowFrontAxis())
        return

    def OnMenuView_CenterShow(self, event):
        """ Show Center Crossメニューのイベント.
          event - wx.MenuEvent.
        """
        self.gfxView.setShowCenterPos(event.IsChecked())
        return

    def OnUpdateMenuView_CenterShow(self, event):
        """ Show Center CrossのUPDATE UIイベント.
          event - wx.UpdateUIEvent.
        """
        event.Check(self.gfxView.getShowCenterPos())
        return

    def OnMenuView_SetBgColor(self, event):
        """ Set Background colorメニューのイベント.
          event - wx.MenuEvent.
        """
        color = self.getBgColor()
        bgc = wx.Colour(int(color[0]*255), int(color[1]*255), int(color[2]*255))
        colData = wx.ColourData()
        colData.SetColour(bgc)
        pBgColorDlg = wx.ColourDialog(self, colData)
        if pBgColorDlg.ShowModal() != wx.ID_OK:
            return
        colData = pBgColorDlg.GetColourData()
        bgc = colData.GetColour()
        color = [bgc.Red()/255.0, bgc.Green()/255.0, bgc.Blue()/255.0, 1.0]
        self.setBgColor(color)
        return

    def OnMenuObj_Selection(self, event):
        """ Select VisObjメニューのイベント.
          event - wx.MenuEvent.
        """
        if not self.app:
            return

        # show ObjSelectDlg
        dlg = ObjSelectDlg.ObjSelectDlg(self)
        if dlg.ShowModal() != wx.ID_OK:
            return
        obj = dlg.getSelectedObj()
        if not obj:
            if self.pObjPropDlg:
                self.pObjPropDlg.Hide()
            return
        
        # show ObjPropDlg
        if self.pObjPropDlg:
            if self.pObjPropDlg.visObj != obj:
                self.pObjPropDlg.Destroy()
                self.pObjPropDlg = None
        if not self.pObjPropDlg:
            self.pObjPropDlg = ObjPropDlg.ObjPropDlg(obj, self)

        self.pObjPropDlg.Show()
        return

    def OnMenuHelp_About(self, event):
        """ Aboutメニューのイベント.
          event - wx.MenuEvent.
        """
        msg = self.app.app_name + ", " + self.app.app_desc + " Version " \
              + self.app.version + "\n" + self.app.copy_right
        title = "About " + self.app.app_name
        wx.MessageBox(msg, title, wx.OK|wx.ICON_INFORMATION)
        return

    def OnToolBar_Normalize(self, event):
        """ ツールバーのNormalizeのイベント.
          event - wx.CommandEvent.
        """
        self.OnMenuView_Normalize(event)
        return

    def OnToolBar_Projection(self, event):
        """ ツールバーのProjection(perspective/parallel)のイベント.
          event - wx.CommandEvent.
        """
        eid = event.GetId()
        if eid == ViewFrameTooBar_ProjPers:
            pm = True
        elif eid == ViewFrameTooBar_ProjOrtho:
            pm = False
        else:
            return
        if self.gfxView.setPerspective(pm):
            self.gfxView.drawArea.chkNotice()
        return

    def OnToolBar_ViewDirs(self, event):
        """ ツールバーのview pointのイベント.
          event - wx.CommandEvent.
        """
        pgv = self.gfxView
        prot = pgv._R
        vp0 = pgv.getViewPoint()
        prot.identity()
        
        eid = event.GetId()
        if eid == ViewFrameTooBar_Back:
            prot.roty(math.pi)
        elif eid == ViewFrameTooBar_Right:
            prot.roty(-math.pi*0.5)
        elif eid == ViewFrameTooBar_Left:
            prot.roty(math.pi*0.5)
        elif eid == ViewFrameTooBar_Top:
            prot.rotx(math.pi*0.5)
        elif eid == ViewFrameTooBar_Bottom:
            prot.rotx(-math.pi*0.5)
        elif eid == ViewFrameTooBar_Front:
            pass

        pgv.normalize()
        if GfxView.s_xformAnim:
            vp1 = pgv.getViewPoint()
            pgv.setViewPoint(vp0)
            pgv.setViewXForm(vp1)

        self.gfxView.sceneGraphUpdated()
        return

    def OnDestroy(self, event):
        if self.pObjPropDlg: self.pObjPropDlg.Destroy()
        if self.pViewPointDlg: self.pViewPointDlg.Destroy()
        if self.gfxView:
            del self.gfxView
            self.gfxView = None
        return

    def OnClose(self, event):
        self.Destroy()
        return
    
