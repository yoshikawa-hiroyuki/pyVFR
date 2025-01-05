#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" DataObj
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]

from vfr import *


class DataObj(gfxGroup.GfxGroup):
    """ DataObjクラス
    """

    def __init__(self, name=gfxNode.Node._NONAME, suicide=False):
        gfxGroup.GfxGroup.__init__(self, name, suicide)

    def getDataType(self):
        return None

    
