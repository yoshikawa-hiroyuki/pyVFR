#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ViewCamera implementation
"""

import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *
from OpenGL.GL import *


#----------------------------------------------------------------------
# ViewCamera class implementation

class ViewCamera(camera.Camera3D):
    """ ViewCameraクラス.
    """

    def __init__(self, suicide =False):
        """ 初期設定.
          suicide - suicideフラグ
        """
        camera.Camera3D.__init__(self, suicide)
        froot = gfxGroup.GfxGroup(name="FRONT", suicide=True)
        self.setFrontNode(froot)

    def addToFront(self, fobj):
        """ オブジェクトの追加.
          fobj - 追加するオブジェクト
        """
        if self._front is None: return False
        return self._front.addChild(fobj)

    def remFromFront(self, fobj):
        """ オブジェクトの削除.
          fobj - 削除するオブジェクト
        """
        if self._front is None: return False
        return self.remChild(fobj)
    
    def dragRot(self, dx, dy):
        """ マウスドラッグによる回転.
          dx - マウス移動量(x)
          dy - マウス移動量(y)
        """
        camera.Camera3D.dragRot(self, dx, dy)
        self.faxis.setRotMatrix(self.getModelMatrix())
        return
