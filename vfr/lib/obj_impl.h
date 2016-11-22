/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/
#ifndef _OBJ_IMPL_H_
#define _OBJ_IMPL_H_

#include "vfr_impl.h"


VFR_CLASS ObjData {
public:
  int nVerts,   nPoolVerts;
  int nNormals, nPoolNormals;
  int nIndices, nPoolIndices;
  int nColors,  nPoolColors;
  vector3*     _verts;
  vector3*     _normals;
  int*         _indices;
  vector4*     _colors;
  vector3      _bbox[2];

  ObjData();
  ~ObjData();
  VFR_BOOL alcPools(const int nV, const int nN, const int nI, const int nC);
  VFR_BOOL alcVerts(const int nv);
  VFR_BOOL alcNormals(const int nn);
  VFR_BOOL alcIndices(const int n);
  VFR_BOOL alcColors(const int nc);
  VFR_BOOL setVert(const int n, const vector3 vv);
  VFR_BOOL setNormal(const int n, const vector3 nv);
  VFR_BOOL setIndice(const int n, const int ind);
  VFR_BOOL setColor3(const int n, const vector3 cv);
  VFR_BOOL setColor4(const int n, const vector4 cv);
  void generateBbox();
};

#endif // _OBJ_IMPL_H_
