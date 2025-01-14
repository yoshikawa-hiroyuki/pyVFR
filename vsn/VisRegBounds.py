#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" VisRegBounds
"""
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *
from VisObj import *


class VisRegBounds(VisObj):
    """ VisRegBoundsクラス
    """

    def __init__(self, data=None, bbox=None, coord=None,
                 name=gfxNode.Node._NONAME):
        if data is None and bbox is None and coord is None:
            raise ValueError("The required argument is not given.")
        VisObj.__init__(self, name)

        if not coord is None:
            self.updateCoord(coord)
        elif not bbox is None:
            self.updateBbox(bbox)
        elif not data is None:
            self.updateData(data)
        self.generateBbox()
        return

    def updateData(self, data):
        self.remAllChildren()
        try:
            nd = len(data.shape)
        except Exception as e:
            raise
        
        ls = lines.Lines()
        if nd >= 3:
            ls.alcData(nV=24)
            x = data.shape[2] - 1.0
            y = data.shape[1] - 1.0
            z = data.shape[0] - 1.0
            pts = ((0.0, 0.0, 0.0), (x, 0.0, 0.0), (x, y, 0.0), (0.0, y, 0.0),
                   (0.0, 0.0, z), (x, 0.0, z), (x, y, z), (0.0, y, z))
            idcs = (0,1,1,2,2,3,3,0, 0,4,1,5,2,6,3,7, 4,5,5,6,6,7,7,4)
            for i in range(len(idcs)):
                ls._verts[i][:] = pts[idcs[i]][:]
                continue
        elif nd == 2:
            ls.alcData(nV=8)
            x = data.shape[1] - 1.0
            y = data.shape[0] - 1.0
            pts = ((0.0, 0.0, 0.0), (x, 0.0, 0.0), (x, y, 0.0), (0.0, y, 0.0))
            idcs = (0,1,1,2,2,3,3,0)
            for i in range(len(idcs)):
                ls._verts[i][:] = pts[idcs[i]][:]
                continue
        elif nd == 1:
            ls.alcData(nV=2)
            x = data.shape[0] - 1.0
            pts = ((0.0, 0.0, 0.0), (x, 0.0, 0.0))
            ls._verts[0][:] = pts[idcs[0]][:]
            ls._verts[1][:] = pts[idcs[1]][:]
        else:
            raise ValueError("The data has invalid shape.")

        ls.generateBbox()
        self.addChild(ls)
        return

    def updateBbox(self, bbox):
        self.remAllChildren()
        if len(bbox) != 2 or len(bbox[0]) != 3:
            raise ValueError("Invalid bbox specified.")

        ls = lines.Lines()
        ls.alcData(nV=24)
        pts = ((bbox[0][0], bbox[0][1], bbox[0][2]),
               (bbox[1][0], bbox[0][1], bbox[0][2]),
               (bbox[1][0], bbox[1][1], bbox[0][2]),
               (bbox[0][0], bbox[1][1], bbox[0][2]),
               (bbox[0][0], bbox[0][1], bbox[1][2]),
               (bbox[1][0], bbox[0][1], bbox[1][2]),
               (bbox[1][0], bbox[1][1], bbox[1][2]),
               (bbox[0][0], bbox[1][1], bbox[1][2]))
        idcs = (0,1,1,2,2,3,3,0, 0,4,1,5,2,6,3,7, 4,5,5,6,6,7,7,4)
        for i in range(len(idcs)):
            ls._verts[i][:] = pts[idcs[i]][:]
            continue
        ls.generateBbox()
        self.addChild(ls)
        return

    def updateCoord(self, coord):
        self.remAllChildren()
        try:
            nd = len(coord.shape)
        except Exception as e:
            raise
        
        if nd < 4 or coord.shape[3] < 3:
            raise ValueError("The coord has invalid shape.")
        nx = data.shape[2]
        ny = data.shape[1]
        nz = data.shape[0]

        # (x0, y0, z0) - (x1, y0, z0)
        ls = lines.LineStrip()
        ls.alcData(nV=nx)
        for i in range(nx):
            ls._verts[i][:] = coord[0, 0, i, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y0, z0) - (x1, y1, z0)
        ls = lines.LineStrip()
        ls.alcData(nV=ny)
        for i in range(ny):
            ls._verts[i][:] = coord[0, i, -1, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y1, z0) - (x0, y1, z0)
        ls = lines.LineStrip()
        ls.alcData(nV=nx)
        for i in range(nx):
            ls._verts[i][:] = coord[0, -1, i, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x0, y1, z0) - (x0, y0, z0)
        ls = lines.LineStrip()
        ls.alcData(nV=ny)
        for i in range(ny):
            ls._verts[i][:] = coord[0, i, 0, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x0, y0, z0) - (x0, y0, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nz)
        for i in range(nz):
            ls._verts[i][:] = coord[i, 0, 0, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y0, z0) - (x1, y0, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nz)
        for i in range(nz):
            ls._verts[i][:] = coord[i, 0, -1, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y1, z0) - (x1, y1, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nz)
        for i in range(nz):
            ls._verts[i][:] = coord[i, -1, -1, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x0, y1, z0) - (x0, y1, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nz)
        for i in range(nz):
            ls._verts[i][:] = coord[i, -1, 0, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        
        # (x0, y0, z1) - (x1, y0, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nx)
        for i in range(nx):
            ls._verts[i][:] = coord[-1, 0, i, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y0, z1) - (x1, y1, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=ny)
        for i in range(ny):
            ls._verts[i][:] = coord[-1, i, -1, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x1, y1, z1) - (x0, y1, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=nx)
        for i in range(nx):
            ls._verts[i][:] = coord[-1, -1, i, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        # (x0, y1, z1) - (x0, y0, z1)
        ls = lines.LineStrip()
        ls.alcData(nV=ny)
        for i in range(ny):
            ls._verts[i][:] = coord[-1, i, 0, :]
            continue
        ls.generateBbox()
        self.addChild(ls)

        return


if __name__ == '__main__':
    import App
    app = App.VsnApp()
    arena = app.getArena()
    
    import numpy as np
    d = np.ndarray([10,20,30])
    bounds = VisRegBounds(data=d)
    arena.addObject(bounds)

    app.run()
    
