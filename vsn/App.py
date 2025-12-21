#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
""" Vsn app main
"""
import os, sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

#----------------------------------------------------------------------
import wx
from ViewFrame import ViewFrame
from Arena import Arena
from vfr import singleton


class VsnApp(wx.App):
    """ Appクラス
    Vsnアプリケーションのメインクラスです．
      _viewFrame: ビューフレーム
      _arena: アリーナ(シーングラフのルート)
    """

    # setup singleton
    __metaclass__ = singleton.Singleton

    
    def __init__(self):
        """ 初期設定.
        """
	# if you want to redirect stdout/stderr, use wx.App.__init__(self)
        wx.App.__init__(self, 0)

        return


    def OnInit(self):
        """ アプリケーション初期化
        wxPythonフレームワークより自動的に呼び出されます．
        """
        self.SetAppName('Vsn')

        # ViewFrame window
        self._viewFrame = ViewFrame(None, -1, "vsn", size=(800,600))
        self._viewFrame.Show(True)
        self._viewFrame.setApp(self)
        self.SetTopWindow(self._viewFrame)

        # Arena
        self._arena = self._viewFrame.gfxView.getArena()

        return True


    def OnCloseApp(self, event):
        """ 終了処理のイベントハンドラ.
        """
        self.Destroy()
        return


    def Refresh(self):
        """ リフレッシュ.
        """
        if not self._viewFrame: return
        self._viewFrame.Refresh()


    def quit(self):
        """ 終了.
        """
        # EPILOGUE
        self.ExitMainLoop()
        return
    

    def reset(self):
        """ リセット.
        """
        # reset the scene
        self._arena.reset()

        # reset the view frame
        self._viewFrame.reset()

        return


    def getViewFrame(self):
        """ ViewFrameの取得.
          戻り値 -> ViewFrame.
        """
        return self._viewFrame

    def getArena(self):
        """ Arenaの取得.
          戻り値 -> Arena.
        """
        return self._arena

    getScene = getArena

    
    def run(self):
        self.MainLoop()


if __name__ == '__main__':
    app = VsnApp()
    app.run()
    

