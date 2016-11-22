# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from OpenGL.GL import *
from PIL import Image
from gfxNode import *


#----------------------------------------------------------------------
# PixelImage class implementation

class PixelImage(GfxNode):
    """
    背景イメージデータクラス
    PixelImageクラスは、カメラの背景に表示するイメージを格納する
    シーングラフノードクラスです．
    Camera.setBgImage()でカメラに登録されると、背景として描画されます．
      imgData: 画像のピクセルデータ
      imgSize: 画像のサイズ[幅×高さ]
      imgDepth: 画像の深さ(1 or 3)
      invY: 上下反転表示フラグ
      fitSize: 表示の際のスケーリングサイズ([0,0]の場合はスケーリングしない)
    """

    def __init__(self, name =Node._NONAME, suicide =False):
        GfxNode.__init__(self, name, suicide)
        self.imgData = None
        self.imgSize = [0, 0]
        self.imgDepth = 0
        self.invY = True
        self.fitSize = [0, 0]
        self._colors[0] = (1.0, 1.0, 1.0, 1.0)

    def isDrawable(self):
        """
        画像が表示可能かどうかを返す
        """
        if not self.imgData: return False
        if self.imgSize[0] < 1 or self.imgSize[1] < 1: return False
        return True

    def renderSolid(self):
        """
        ソリッドレンダリング
        画像のOpenGL描画(glDrawPixels)を行います．
        invYがTrueの場合は上下を反転して描画します．またfitSizeが[0,0]でない
        場合は，fitSizeにスケーリングして描画します．
        """
        if not self.isDrawable(): return
        if self.fitSize[0] > 0 and self.fitSize[1] > 0:
            if self.invY:
                glRasterPos3f(-1.0, 1.0, -1.0)
                glPixelZoom(float(self.fitSize[0])/self.imgSize[0],
                            -float(self.fitSize[1])/self.imgSize[1])
            else:
                glRasterPos3f(-1.0, -1.0, -1.0)
                glPixelZoom(float(self.fitSize[0])/self.imgSize[0],
                            float(self.fitSize[1])/self.imgSize[1])
        else:
            if self.invY:
                glRasterPos3f(-1.0, 1.0, -1.0)
                glPixelZoom(1.0, -1.0)
            else:
                glRasterPos3f(-1.0, -1.0, -1.0)
                glPixelZoom(1.0, 1.0)

        # set color and face mode (failsafe)
        glColor4fv(self._colors[0])
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # display-list check
        if self.beginDispList(DLF_SOLID): return

        # set pixel store mode
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # draw pixels
        if self.imgDepth == 1:
            glDrawPixels(self.imgSize[0], self.imgSize[1],
                         GL_LUMINANCE, GL_UNSIGNED_BYTE, self.imgData)
        elif self.imgDepth == 3:
            glDrawPixels(self.imgSize[0], self.imgSize[1],
                         GL_RGB, GL_UNSIGNED_BYTE, self.imgData)

        # end display-list definition
        self.endDispList(DLF_SOLID)

        return

    def loadImage(self, path):
        """
        イメージデータのロード
        指定されたイメージファイルより画像データをロードします．
        - path: イメージファイルのパス
        """
        image = Image.open(path).convert("RGB")
        self.setImage(image)

    def setImage(self, image):
        """
        イメージデータの設定
        PILモジュールのImageクラスのデータを画像データとして設定します．
        - image: Imageクラスデータ
        """
        imgData = image.tostring()
        imgSize = image.size
        self.setImageData(imgData, imgSize[0], imgSize[1])

    def setImageData(self, data, width, height):
        """
        イメージデータの設定
        バイナリデータを画像データとして設定します．
        - data: バイナリデータ(サイズは width×height または width×height×3)
        - width: 画像の幅
        - height: 画像の高さ
        """
        self.imgData = data
        self.imgSize = [width, height]
        if len(self.imgData) == self.imgSize[0] * self.imgSize[1]:
            self.imgDepth = 1
        elif len(self.imgData) == self.imgSize[0] * self.imgSize[1] * 3:
            self.imgDepth = 3
        else:
            self.imgData = None
            self.imgSize = [0, 0]
            self.imgDepth = 0
            return
        self.notice(True)
    
    def setFitSize(self, width =-1, height =-1):
        """
        表示スケーリングサイズの設定
        表示の際のスケーリングサイズを設定します．
        [0,0]の場合はスケーリングされません．
        - width: スケーリングサイズの幅(負値の場合は現在の値を変更しない)
        - height: スケーリングサイズの高さ(負値の場合は現在の値を変更しない)
        """
        if width >= 0:
            self.fitSize[0] = width
        if height >= 0:
            self.fitSize[1] = height
        if width >= 0 or height >= 0:
            self.notice()
        return
