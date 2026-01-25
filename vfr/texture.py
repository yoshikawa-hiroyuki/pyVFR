#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from .image import *
from .node import *
from .utilMath import *


class TexNode(Base):
    """
    テクスチャデータクラス
    """
    (TEX_NOMAP, TEX_XYP, TEX_YZP, TEX_ZXP) = range(4)
    _pX0 = [1.0, 0.0, 0.0, 0.0]
    _pY0 = [0.0, 1.0, 0.0, 0.0]
    _pZ0 = [0.0, 0.0, 1.0, 0.0]

    def __init__(self, **args):
        Base.__init__(self, **args)
        self._pixImage = None
        self._matrix = Mat4()
        self._bbox = [Vec3(), Vec3((1,1,1))]
        self._texId = 0
        self._mapType = TexNode.TEX_XYP
        return

    def __del__(self):
        try:
            if glIsTexture(self._texId):
                glDeleteTextures(1, [self._texId])
        except:
            pass
        return

    def setImage(self, image):
        if not image or not image.isDrawable:
            return False

        if glIsTexture(self._texId):
            glDeleteTextures(1, [self._texId])
        self._texId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texId)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

        if image.imgDepth == 3:
            glTexImage2D(GL_TEXTURE_2D, 0,
                         GL_RGB, image.imgSize[0], image.imgSize[1], 0,
                         GL_RGB, GL_UNSIGNED_BYTE, image.imgData)
        elif image.imgDepth == 1:
            glTexImage2D(GL_TEXTURE_2D, 0,
                         GL_LUMINANCE, image.imgSize[0], image.imgSize[1], 0,
                         GL_LUMINANCE, GL_UNSIGNED_BYTE, image.imgData)
        else:
            return False
        self._pixImage = image

        self.notice()
        return True

    def setMapType(self, mt):
        if self._mapType == mt: return True
        if not mt in (TexNode.TEX_NOMAP, TexNode.TEX_XYP,
                      TexNode.TEX_YZP, TexNode.TEX_ZXP):
            return False
        self._mapType = mt
        self.notice()
        return True

    def setBbox(self, min, max):
        self._bbox[0][:] = min[:]
        self._bbox[1][:] = max[:]
        self.notice()
        return
    
    def enable(self):
        if self._mapType == TexNode.TEX_NOMAP:
            return True
        if not self._pixImage:
            return False
        if not glIsTexture(self._texId):
            return False
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._texId)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR);
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR);

        (spanS, spanT) = (1.0, 1.0)
        tV = [0.0, 0.0, 0.0]
        if self._mapType == TexNode.TEX_XYP:
            glTexGenfv(GL_S, GL_OBJECT_PLANE, TexNode._pX0)
            glTexGenfv(GL_T, GL_OBJECT_PLANE, TexNode._pY0)
            spanS = self._bbox[1][0] - self._bbox[0][0]
            spanT = self._bbox[1][1] - self._bbox[0][1]
            tV[0] = -self._bbox[0][0]
            tV[1] = -self._bbox[0][1]
        elif self._mapType == TexNode.TEX_YZP:
            glTexGenfv(GL_S, GL_OBJECT_PLANE, TexNode._pY0)
            glTexGenfv(GL_T, GL_OBJECT_PLANE, TexNode._pZ0)
            spanS = self._bbox[1][1] - self._bbox[0][1]
            spanT = self._bbox[1][2] - self._bbox[0][2]
            tV[0] = -self._bbox[0][1]
            tV[1] = -self._bbox[0][2]
        elif self._mapType == TexNode.TEX_ZXP:
            glTexGenfv(GL_S, GL_OBJECT_PLANE, TexNode._pZ0)
            glTexGenfv(GL_T, GL_OBJECT_PLANE, TexNode._pX0)
            spanS = self._bbox[1][2] - self._bbox[0][2]
            spanT = self._bbox[1][0] - self._bbox[0][0]
            tV[0] = -self._bbox[0][2]
            tV[1] = -self._bbox[0][0]
        else:
            return False
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        if spanS > 1e-8 and spanT > 1e-8:
            glScalef(1.0/spanS, 1.0/spanT, 1.0)
        glTranslatef(tV[0], tV[1], tV[2])
        
        glMultMatrixf(self._matrix.m_v)
        glMatrixMode(GL_MODELVIEW)
        return True

    def disable(self):
        if self._mapType == TexNode.TEX_NOMAP:
            return
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_TEXTURE_2D)
        return

    
    
