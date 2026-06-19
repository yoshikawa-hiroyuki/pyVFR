#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisRegVolren
"""
import sys, os
import numpy as np
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from svr import *
from VisRegularMesh import *


#----------------------------------------------------------------------
class VisRegVolren(VisRegularMesh):
    """ VisRegVolrenクラス
        show volume rendering of regular mesh
    """

    
