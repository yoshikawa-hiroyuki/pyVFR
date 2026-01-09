#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisObj selection dialog implementation
"""

import sys, os
import wx
if not ".." in sys.path:
    sys.path = sys.path + [".."]
import Arena


class ObjSelectDlg(wx.Dialog):
    """ ObjSelectDlgクラス.
    """

    def __init__(self, parent, ID=-1, title='ObjSelect', exceptId=-1,
                 pos=wx.DefaultPosition, size=(400, 300)):
        """ 初期設定.
          parent - wx.Window. parent window.
          ID - int. id.
          title - String. 表題.
          pos - Point. position.
          size - Size. size.
        """
        super().__init__(parent, title=title, size=size, pos=pos)
        self.parent = parent
        self.exceptId = exceptId

        panel = wx.Panel(self)

        self.listCtl \
            = wx.ListCtrl(panel,
                          style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN)
        self.listCtl.InsertColumn(0, "Type", width=100)
        self.listCtl.InsertColumn(1, "Name", width=200)

        # update list
        self.updateList()

        # buttons
        okBtn = wx.Button(panel, wx.ID_OK)
        cancelBtn = wx.Button(panel, wx.ID_CANCEL)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listCtl, 1, wx.EXPAND | wx.ALL, 10)
        sizerH = wx.BoxSizer()
        sizerH.Add(okBtn, flag=wx.ALL, border=3)
        sizerH.Add(cancelBtn, flag=wx.ALL, border=3)
        sizer.Add(sizerH, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        return

    
    def updateList(self):
        if not self.listCtl:
            return
        self.listCtl.DeleteAllItems()

        arena = Arena.GetArena()
        if not arena:
            return

        numObj = arena.getNumObject()
        idx = 0
        for n in range(numObj):
            obj = arena.getObject(n)
            if not obj:
                continue
            if obj.getID() == self.exceptId:
                continue
            self.listCtl.InsertItem(idx, obj.getVisObjType())
            self.listCtl.SetItem(idx, 1, obj.getName())
            idx += 1
            continue # end of for n

        return

    
    def getSelectedObj(self):
        if not self.listCtl:
            return None
        if not self.parent or not self.parent.isViewFrame():
            return None
        
        idx = self.listCtl.GetFirstSelected()
        if idx < 0:
            return None
        arena = self.parent.getArena()
        if not arena:
            return None
        obj = arena.getObject(idx)
        return obj


if __name__ == '__main__':
    app = wx.App()
    dlg = ObjSelectDlg(None)
    dlg.Show()
    app.MainLoop()
