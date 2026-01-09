#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
""" Vsn app main
"""
import os, sys
import contextlib
if not ".." in sys.path:
    sys.path = sys.path + [".."]

    
#----------------------------------------------------------------------
# Suppressing ‘warning logs’ in the macOS OpenGL implementation

@contextlib.contextmanager
def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


#----------------------------------------------------------------------
import wx
import code
import threading

import ViewFrame
from Arena import Arena


class VsnApp(wx.App):
    """ Appクラス
    Vsnアプリケーションのメインクラスです．
      _viewFrame: ビューフレーム
      _arena: アリーナ(シーングラフのルート)
    """

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
        self._viewFrame = ViewFrame.ViewFrame(None, -1, "vsn", size=(800,600))
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

    # equivalent to getArena()
    getScene = getArena

    @staticmethod
    def console_procedure():
        console = code.InteractiveConsole(locals())
        console.interact("Custom interactive console. Type Python code here.")

    @staticmethod
    def run_console():
        threading.Thread(target=VsnApp.console_procedure, daemon=True).start()
    
    def run(self, debug=False):
        if debug:
            self.MainLoop()
        else:
            with suppress_stderr():
                self.MainLoop()


if __name__ == '__main__':
    app = VsnApp()
    app.run_console()
    app.run()
    

