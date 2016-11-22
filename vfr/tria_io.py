#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
from triangles import *
from utilMath import *
import struct

#----------------------------------------------------------------------
def IsStlAscii(path):
    """
    指定されたSTLファイルがASCIIかBINARYかの判定を行い，結果を返す関数です．
    ASCIIの場合は1を，BINARYの場合は0を，エラーの場合は-1を返します．
    - path: STLファイルのパス
    """
    try:
        f = open(path, 'r')
        f.read(80)
        nf = struct.unpack('i', f.read(4))[0]
        f.close()
    except:
        return -1 # error
    if nf < 0 or nf > 500000000:
        return 1 # ascii
    return 0 # binary

#----------------------------------------------------------------------
def Read(path, fmt =None):
    """
    指定された形状ファイルを読み込み，対応するTrianglesノードを生成して返す
    関数です．戻り値は生成したTrianglesノードとフォーマット文字列のタプルです．
    - path: 形状ファイルのパス
    - fmt: 形状ファイルのフォーマット．以下のいずれかの文字列で指定する．
        Wavefront OBJ: 'obj', STL Ascii: 'sla', STL Binary: 'slb'
        Noneの場合はpathのサフィックスから判定する．
    """
    if not path or len(path) < 1: return (None, '')
    xfmt = None
    if fmt : xfmt = fmt
    else:
        if not xfmt:
            for s in (".obj", ".wfo", ".OBJ", ".WFO"):
                if path.endswith(s):
                    xfmt = 'obj'; break
        if not xfmt:
            for s in (".sla", ".stla", ".SLA", ".STLA"):
                if path.endswith(s):
                    xfmt = 'sla'; break
        if not xfmt:
            for s in (".slb", ".stlb", ".SLB", ".STLB"):
                if path.endswith(s):
                    xfmt = 'slb'; break
        if not xfmt:
            if path.endswith(".stl") or path.endswith(".STL"):
                if IsStlAscii(path) == 1:
                    xfmt = 'sla'
                else:
                    xfmt = 'slb'
    if xfmt == 'obj':
        return (ReadOBJ(path), 'obj')
    if xfmt == 'sla':
        return (ReadSLA(path), 'sla')
    if xfmt == 'slb':
        return (ReadSLB(path), 'slb')
    return None

def Write(tria, path, fmt =None):
    """
    指定されたTrianglesノードの頂点および法線ベクトルデータを，指定された
    形状ファイルに出力します．成功した場合はTrueを返します．
    Trianglesノードは，3つ以上の頂点を持っている必要があります．
    また，法線ベクトルを持たない場合は，全ての法線ベクトルを(0,0,1)として
    出力します．
    - tria: Trianglesノード
    - path: 形状ファイルのパス
    - fmt: 形状ファイルのフォーマット．以下のいずれかの文字列で指定する．
        Wavefront OBJ: 'obj', STL Ascii: 'sla', STL Binary: 'slb'
        Noneの場合はpathのサフィックスから判定する．
    """
    if not path or len(path) < 1: return False
    xfmt = None
    if fmt : xfmt = fmt
    else:
        if not xfmt:
            for s in (".obj", ".wfo", ".OBJ", ".WFO"):
                if path.endswith(s):
                    xfmt = 'obj'; break
        if not xfmt:
            for s in (".sla", ".stla", ".SLA", ".STLA"):
                if path.endswith(s):
                    xfmt = 'sla'; break
        if not xfmt:
            for s in (".slb", ".stlb", ".SLB", ".STLB"):
                if path.endswith(s):
                    xfmt = 'slb'; break
        if not xfmt:
            if path.endswith(".stl") or path.endswith(".STL"):
                #xfmt = 'sla'
                xfmt = 'slb'
    if xfmt == 'obj':
        return WriteOBJ(tria, path)
    if xfmt == 'sla':
        return WriteSLA(tria, path)
    if xfmt == 'slb':
        return WriteSLB(tria, path)
    return False


#----------------------------------------------------------------------
# STL/Ascii interface

def ReadSLA(path):
    """
    SLA(STL Ascii)ファイルの入力
    指定されたSLAファイルを入力し，対応するTrianglesノードを生成して返します．
    - path: SLAファイルのパス
    """
    tria = Triangles()
    if not tria.loadFile(path, 'sla'):
        del tria
        return None
    tria._normalMode = AT_PER_VERTEX
    return tria


def WriteSLA(tria, path):
    """
    TrianglesノードからSLA(STL Ascii)ファイルへの出力
    指定されたTrianglesノードの頂点および法線ベクトルデータを，指定された
    SLAファイルに出力します．成功した場合はTrueを返します．
    Trianglesノードは，3つ以上の頂点を持っている必要があります．
    また，法線ベクトルを持たない場合は，全ての法線ベクトルを(0,0,1)として
    出力します．
    - tria: Trianglesノード
    - path: SLAファイルのパス
    """
    if tria is None:
        return False
    if not '_GfxNode__useDispList' in dir(tria):
        return False
    if tria.getNumVerts() < 3:
        return False
    
    try:
        f = open(path, 'w')
    except:
        return False
    f.write('solid ascii\n')

    nn = tria.getNumNormals()
    nf = tria.getNumVerts() / 3
    for i in range(nf):
        if tria._normalMode == AT_PER_VERTEX:
            if i*3+2 < nn:
                nml = Vec3(tria._normals[i*3]) + \
                    Vec3(tria._normals[i*3+1]) + Vec3(tria._normals[i*3+2])
                nml = nml * (1/3.0)
            else:
                nml = (0.0, 0.0, 1.0)
            f.write('facet normal %f %f %f\n' % (nml[0], nml[1], nml[2]))
        elif tria._normalMode == AT_PER_FACE:
            if i < nn:
                f.write('facet normal %f %f %f\n' % (tria._normals[i][0],
                                                     tria._normals[i][1],
                                                     tria._normals[i][2]))
            else:
                f.write('facet normal 0.0 0.0 1.0\n')
        else:
            f.write('facet normal 0.0 0.0 1.0\n')

        f.write('outer loop\n')
        f.write('vertex %f %f %f\n' % (tria._verts[i*3  ][0],
                                       tria._verts[i*3  ][1],
                                       tria._verts[i*3  ][2]))
        f.write('vertex %f %f %f\n' % (tria._verts[i*3+1][0],
                                       tria._verts[i*3+1][1],
                                       tria._verts[i*3+1][2]))
        f.write('vertex %f %f %f\n' % (tria._verts[i*3+2][0],
                                       tria._verts[i*3+2][1],
                                       tria._verts[i*3+2][2]))
        f.write('endloop\n')
        f.write('endfacet\n')

    f.close()
    return True


#----------------------------------------------------------------------
# STL/Binary interface

def ReadSLB(path):
    """
    SLB(STL Binary)ファイルの入力
    指定されたSLBファイルを入力し，対応するTrianglesノードを生成して返します．
    - path: SLBファイルのパス
    """
    tria = Triangles()
    if not tria.loadFile(path, 'slb'):
        del tria
        return None
    tria._normalMode = AT_PER_VERTEX
    return tria


def WriteSLB(tria, path):
    """
    TrianglesノードからSLB(STL Binary)ファイルへの出力
    指定されたTrianglesノードの頂点および法線ベクトルデータを，指定された
    SLBファイルに出力します．成功した場合はTrueを返します．
    Trianglesノードは，3つ以上の頂点を持っている必要があります．
    また，法線ベクトルを持たない場合は，全ての法線ベクトルを(0,0,1)として
    出力します．
    - tria: Trianglesノード
    - path: SLBファイルのパス
    """
    if tria is None:
        return False
    if not '_GfxNode__useDispList' in dir(tria):
        return False
    nv = tria.getNumVerts()
    nf = nv / 3
    if nf < 1:
        return False
    nn = tria.getNumNormals()
    
    try:
        f = open(path, 'wb')
    except:
        return False

    # write header(80bytes)
    f.write(struct.pack('80s', 'created by using tria_io.WriteSLB'))

    # write data
    f.write(struct.pack('i', nf))
    for i in range(nf):
        if tria._normalMode == AT_PER_VERTEX:
            if i*3+2 < nn:
                nml = Vec3(tria._normals[i*3]) + \
                    Vec3(tria._normals[i*3+1]) + Vec3(tria._normals[i*3+2])
                nml = nml * (1/3.0)
            else:
                nml = (0.0, 0.0, 1.0)
            f.write(struct.pack('fff', nml[0], nml[1], nml[2]))
        elif tria._normalMode == AT_PER_FACE:
            if i < nn:
                f.write(struct.pack('fff', tria._normals[i][0],
                                    tria._normals[i][1], tria._normals[i][2]))
            else:
                f.write(struct.pack('fff', 0.0, 0.0, 1.0))
        else:
            f.write(struct.pack('fff', 0.0, 0.0, 1.0))

        f.write(struct.pack('fff', tria._verts[i*3  ][0],
                            tria._verts[i*3  ][1], tria._verts[i*3  ][2]))
        f.write(struct.pack('fff', tria._verts[i*3+1][0],
                            tria._verts[i*3+1][1], tria._verts[i*3+1][2]))
        f.write(struct.pack('fff', tria._verts[i*3+2][0],
                            tria._verts[i*3+2][1], tria._verts[i*3+2][2]))
        f.write(struct.pack('cc', '\0', '\0'))

    f.close()
    return True


#----------------------------------------------------------------------
# Wavefront OBJ interface

def ReadOBJ(path):
    """
    Alias|Wavefront OBJファイルの入力
    指定されたOBJファイルを入力し，対応するTrianglesノードを生成して返します．
    - path: OBJファイルのパス
    """
    tria = Triangles()
    if not tria.loadFile(path, 'obj'):
        del tria
        return None

    tria._normalMode = AT_PER_VERTEX
    if tria.nNormals != tria.nVerts:
        tria.generateNormals()
    return tria


def WriteOBJ(tria, path):
    """
    TrianglesノードからOBJファイルへの出力
    指定されたTrianglesノードの頂点および法線ベクトルデータを，指定された
    OBJファイルに出力します．成功した場合はTrueを返します．
    Trianglesノードは，3つ以上の頂点を持っている必要があります．
    また，法線ベクトルを持たない場合は，全ての法線ベクトルを(0,0,1)として
    出力します．
    - tria: Trianglesノード
    - path: OBJファイルのパス
    """
    if tria is None:
        return False
    if not '_GfxNode__useDispList' in dir(tria):
        return False

    nv = tria.getNumVerts()
    nn = tria.getNumNormals()
    if nv < 3:
        return False
    nf = nv / 3
    if nn >= nv and tria._normalMode == AT_PER_VERTEX:
        hasNml = True
    else:
        hasNml = False
    
    try:
        f = open(path, 'w')
    except:
        return False

    # write vertices
    for i in range(nv):
        f.write('v %f %f %f\n' % (tria._verts[i][0],
                                  tria._verts[i][1],
                                  tria._verts[i][2]))
    # write normals
    if hasNml:
        for i in range(nn):
            f.write('vn %f %f %f\n' % (tria._normals[i][0],
                                       tria._normals[i][1],
                                       tria._normals[i][2]))
    # write faces
    if hasNml:
        for i in range(nf):
            f.write('f %d//%d %d//%d %d//%d\n' %
                    (i*3+1, i*3+1, i*3+2, i*3+2, i*3+3, i*3+3))
    else:
        for i in range(nf):
            f.write('f %d %d %d\n' % (i*3+1, i*3+2, i*3+3))

    f.close()
    return True
